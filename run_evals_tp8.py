"""TP=8 single-job eval runner for large models on an 8×A100 80GB node.

Runs lm_eval with vllm tensor_parallel_size=8, one model at a time across all
8 GPUs. With only one TP group on the node we keep CUDA graphs and the custom
all-reduce kernel enabled (the workarounds in run_evals_tp2.py exist only
because multiple TP groups collided on P2P registrations and OOM'd during
graph capture).

Selection: every (not-yet-done) row in the input CSV runs at TP=8 — the CSV
is the curated large list (see models_to_run_large.csv), so we trust it
instead of recomputing from `params`. The `large` flag is ignored here since
this runner *is* the large-model path.

Usage:
    python run_evals_tp8.py                       # uses models_to_run_large.csv
    MODELS_CSV=/path/to/other.csv python run_evals_tp8.py
    DRY_RUN=1 python run_evals_tp8.py             # list models, don't run
"""

import glob
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path


# run_evals reads MODELS_CSV at import time, so set the large default first.
os.environ.setdefault("MODELS_CSV", "models_to_run_large.csv")

from huggingface_hub import HfApi

from run_evals import (
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


TP_SIZE = 8
GPU_IDS = "0,1,2,3,4,5,6,7"

# Track the running lm_eval Popen so SIGINT can kill the whole tree. vLLM's
# spawn-based workers survive a wrapper crash and leak GPU memory otherwise.
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


def run_model_tp8(model_path: str, task: str) -> Path | None:
    output_dir = RESULTS_DIR / model_slug(model_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_args = (
        f"pretrained={model_path},max_model_len=8192,tensor_parallel_size={TP_SIZE}"
    )

    cmd = [
        "lm_eval",
        "--model",
        "vllm",
        "--model_args",
        model_args,
        "--tasks",
        task,
        "--batch_size",
        "auto",
        "--output_path",
        str(output_dir),
        "--apply_chat_template",
        "--log_samples",
    ]
    if CUSTOM_TASK_DIR:
        cmd += ["--include_path", str(CUSTOM_TASK_DIR)]

    env = os.environ.copy()
    env["HF_DATASETS_OFFLINE"] = "1"
    env["CUDA_VISIBLE_DEVICES"] = GPU_IDS
    if HF_TOKEN_READ:
        env["HF_TOKEN"] = HF_TOKEN_READ

    print(
        f"\n  ▶ {model_path}  [task={task} | TP={TP_SIZE} | GPUs {GPU_IDS}]", flush=True
    )

    proc = subprocess.Popen(cmd, env=env, start_new_session=True)
    pgid = proc.pid
    with _live_lock:
        _live_procs.add(proc)
    try:
        rc = proc.wait()
    finally:
        with _live_lock:
            _live_procs.discard(proc)
        try:
            os.killpg(pgid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    if rc != 0:
        print(
            f"  [ERROR] lm_eval exited {rc} for {model_path} "
            f"(see log above for the traceback)"
        )
        return None

    results = sorted(
        glob.glob(str(output_dir / "**" / "results_*.json"), recursive=True)
    )
    if not results:
        print(f"  [ERROR] No result JSON found for {model_path}")
        return None

    latest = Path(results[-1])
    print(f"  ■ {model_path} → {latest.name}")
    return latest


def main() -> int:
    if not HF_TOKEN_WRITE:
        raise OSError("Set HF_TOKEN_WRITE: export HF_TOKEN_WRITE=hf_...")
    if not HF_TOKEN_READ:
        print("[WARN] HF_TOKEN_READ not set — gated models may fail to download")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    api = HfApi(token=HF_TOKEN_WRITE)

    df = load_models(CSV_PATH)

    print("\nChecking HF for completed evals...")
    done = fetch_completed(api)
    if done:
        print(f"  Already done ({len(done)}): {sorted(done)}")
    df = df[~df["model_path"].isin(done)].copy()
    print(f"  Remaining after HF filter: {len(df)}")

    if df.empty:
        print("Nothing to run.")
        return 0

    print(f"\n{'=' * 60}")
    print(f"Running {len(df)} model(s) sequentially at TP={TP_SIZE}")
    for _, row in df.iterrows():
        print(
            f"  - {row['model_path']}  task={row['task']}  params={row.get('params_b', '?')}B"
        )

    if os.environ.get("DRY_RUN"):
        print("\nDRY_RUN=1 — not running.")
        return 0

    print()
    for _, row in df.iterrows():
        try:
            result = run_model_tp8(row["model_path"], row["task"])
            if result:
                upload(api, result, row["model_path"])
        except Exception as e:
            print(f"  [ERROR] {row['model_path']}: {e}")

    print(f"\n{'=' * 60}")
    print("All TP=8 evals complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
