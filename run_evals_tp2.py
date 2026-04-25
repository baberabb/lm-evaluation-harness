"""
TP=2 multi-GPU eval runner for medium-sized models.

Runs lm_eval with vllm tensor_parallel_size=2 across NUMA-safe GPU pairs.
On this node GPUs 0-3 are NUMA 0 and 4-7 are NUMA 1 (nvidia-smi topo -m),
so we use the four fixed pairs (0,1), (2,3), (4,5), (6,7) and never cross
the SYS interconnect.

Selection: every (non-large, not-yet-done) row in the input CSV runs with
TP=2 — the CSV is the curated medium list, so we trust it instead of
recomputing from `params`. 1-GPU models should go through
run_evals_scheduler.py; >2-GPU models need a separate tp4/tp8 runner.

Usage:
    python run_evals_tp2.py                       # uses models_to_run_medium.csv
    MODELS_CSV=/path/to/other.csv python run_evals_tp2.py
    DRY_RUN=1 python run_evals_tp2.py             # list models, don't run
"""

import glob
import os
import signal
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# run_evals reads MODELS_CSV at import time and load_models() runs at module
# top level, so set the medium default before importing.
os.environ.setdefault("MODELS_CSV", "models_to_run_medium.csv")

from huggingface_hub import HfApi  # noqa: E402

from run_evals import (  # noqa: E402
    CSV_PATH,
    CUSTOM_TASK_DIR,
    HF_TOKEN_READ,
    HF_TOKEN_WRITE,
    RESULTS_DIR,
    fetch_completed,
    load_models,
    model_slug,
    upload,
)

# NUMA-safe TP=2 pairs on this 8×GPU node.
GPU_PAIRS = [(0, 1), (2, 3), (4, 5), (6, 7)]


# Track every running lm_eval Popen so SIGINT can kill the whole tree. Without
# this, vLLM's `spawn`-based worker subprocesses survive when the wrapper dies
# and leak GPU memory (see medium1.log incidents).
_live_procs: set[subprocess.Popen] = set()
_live_lock = threading.Lock()


def _kill_all_groups(signum, _frame):
    name = signal.Signals(signum).name
    with _live_lock:
        procs = list(_live_procs)
    print(f"\n[SIGNAL] {name} — killing {len(procs)} subprocess group(s)", flush=True)
    for p in procs:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
    sys.exit(128 + signum)


signal.signal(signal.SIGINT, _kill_all_groups)
signal.signal(signal.SIGTERM, _kill_all_groups)


class PairPool:
    """Thread-safe pool of GPU pairs; acquire() blocks until one is free."""

    def __init__(self, pairs):
        self.free = list(pairs)
        self._cond = threading.Condition(threading.Lock())

    def acquire(self):
        with self._cond:
            while not self.free:
                self._cond.wait()
            return self.free.pop(0)

    def release(self, pair):
        with self._cond:
            self.free.append(pair)
            self._cond.notify_all()


def run_model_tp2(model_path: str, task: str, gpu_pair: tuple[int, int]) -> Path | None:
    output_dir = RESULTS_DIR / model_slug(model_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # disable_custom_all_reduce: vLLM's custom P2P all-reduce kernel fails with
    # "custom_all_reduce.cuh:455 'invalid argument'" when several TP groups run
    # on one host (P2P registrations collide). NCCL all-reduce is safe.
    # enforce_eager + max_model_len=6144: 27-32B bf16 models on 48 GB cards
    # with TP=2 OOM during CUDA graph capture; eager skips graphs (~5 GB/GPU)
    # and the smaller context shrinks the KV cache budget.
    model_args = (
        f"pretrained={model_path},"
        f"max_model_len=6144,"
        f"tensor_parallel_size=2,"
        f"disable_custom_all_reduce=True,"
        f"enforce_eager=True"
    )

    cmd = [
        "lm_eval",
        "--model", "vllm",
        "--model_args", model_args,
        "--tasks", task,
        "--batch_size", "auto",
        "--output_path", str(output_dir),
        "--apply_chat_template",
        "--log_samples",
    ]
    if CUSTOM_TASK_DIR:
        cmd += ["--include_path", str(CUSTOM_TASK_DIR)]

    env = os.environ.copy()
    env["HF_DATASETS_OFFLINE"] = "1"
    env["CUDA_VISIBLE_DEVICES"] = f"{gpu_pair[0]},{gpu_pair[1]}"
    env["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
    if HF_TOKEN_READ:
        env["HF_TOKEN"] = HF_TOKEN_READ

    print(f"\n  ▶ {model_path}  [task={task} | GPUs {gpu_pair[0]},{gpu_pair[1]}]", flush=True)

    # start_new_session=True puts lm_eval in its own process group, so we can
    # killpg() the whole tree (including vLLM workers) on Ctrl-c or after a
    # crash — otherwise spawn-method workers detach and orphan GPU memory.
    # Stdio is inherited so lm_eval/vLLM logs stream live to tee.
    proc = subprocess.Popen(cmd, env=env, start_new_session=True)
    pgid = proc.pid  # session leader: pgid == pid
    with _live_lock:
        _live_procs.add(proc)
    try:
        rc = proc.wait()
    finally:
        with _live_lock:
            _live_procs.discard(proc)
        # Belt-and-suspenders: clean exit → group is empty (no-op);
        # crash/CUDA error → reaps any vLLM workers that detached.
        try:
            os.killpg(pgid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    if rc != 0:
        print(f"  [ERROR] lm_eval exited {rc} for {model_path} "
              f"(see log above for the traceback)")
        return None

    results = sorted(glob.glob(str(output_dir / "**" / "results_*.json"), recursive=True))
    if not results:
        print(f"  [ERROR] No result JSON found for {model_path}")
        return None

    latest = Path(results[-1])
    print(f"  ■ {model_path} → {latest.name}")
    return latest


def main() -> int:
    if not HF_TOKEN_WRITE:
        raise EnvironmentError("Set HF_TOKEN_WRITE: export HF_TOKEN_WRITE=hf_...")
    if not HF_TOKEN_READ:
        print("[WARN] HF_TOKEN_READ not set — gated models may fail to download")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    api = HfApi(token=HF_TOKEN_WRITE)

    df = load_models(CSV_PATH)
    n_total = len(df)

    # 1. Drop large-flagged models.
    df = df[df["large"] != 1].copy()
    print(f"\nAfter large-flag filter: {len(df)}  (dropped {n_total - len(df)})")

    # 2. Drop models already on HF.
    print("\nChecking HF for completed evals...")
    done = fetch_completed(api)
    if done:
        print(f"  Already done ({len(done)}): {sorted(done)}")
    df = df[~df["model_path"].isin(done)].copy()
    print(f"  Remaining after HF filter: {len(df)}")

    # 3. Flag rows whose params suggest >2 GPUs (informational — we still run
    #    them at TP=2 since the CSV is curated).
    big = df[df["n_gpus"] > 2]
    if not big.empty:
        print(f"\nNote: {len(big)} model(s) have params suggesting >2 GPUs — "
              f"running at TP=2 anyway (may OOM):")
        for _, row in big.iterrows():
            print(f"  - {row['model_path']}  ({row.get('params_b','?')}B, n_gpus={row['n_gpus']})")

    print(f"\nTP=2 models to run: {len(df)}")

    if df.empty:
        print("Nothing to run.")
        return 0

    print(f"\n{'='*60}")
    print(f"Running {len(df)} models on {len(GPU_PAIRS)} NUMA-safe pairs: {GPU_PAIRS}")

    if os.environ.get("DRY_RUN"):
        print("\nDRY_RUN=1 — listing models instead of running:\n")
        for _, row in df.iterrows():
            print(f"  {row['model_path']}  task={row['task']}  params={row.get('params_b','?')}B")
        return 0

    pool = PairPool(GPU_PAIRS)

    def run_with_pair(model_path, task):
        pair = pool.acquire()
        try:
            return run_model_tp2(model_path, task, pair)
        finally:
            pool.release(pair)

    with ThreadPoolExecutor(max_workers=len(GPU_PAIRS)) as ex:
        futures = {
            ex.submit(run_with_pair, row["model_path"], row["task"]): row["model_path"]
            for _, row in df.iterrows()
        }
        for f in as_completed(futures):
            model_path = futures[f]
            try:
                result = f.result()
                if result:
                    upload(api, result, model_path)
            except Exception as e:
                print(f"  [ERROR] {model_path}: {e}")

    print(f"\n{'='*60}")
    print("All TP=2 evals complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
