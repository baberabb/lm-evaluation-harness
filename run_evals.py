"""
Multi-GPU parallel evaluation runner.

Task routing:
  type=instruct → global_piqa_generation
  type=base     → global_piqa_cloze

Strategy:
- All models run one-per-GPU in parallel (8× 80GB, everything fits on 1 GPU)
- Models with large=1 are skipped
- Results checked on HF before running; uploaded immediately after each model

Required CSV columns: model_path, type, large
All other columns (params, family, languages, ...) are ignored.

Usage:
    pip install lm_eval vllm huggingface_hub pandas
    export HF_TOKEN=hf_...
    python run_evals.py                          # uses models_to_run.csv
    MODELS_CSV=/path/to/other.csv python run_evals.py
"""

import os
import glob
import math
import subprocess
import threading
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from huggingface_hub import HfApi, list_repo_files
from huggingface_hub.utils import RepositoryNotFoundError

# ── Config (edit these) ───────────────────────────────────────────────────────
NUM_GPUS        = 8          # total GPUs on this node
VRAM_PER_GPU_GB = 48         # VRAM per GPU in GB (49140 MiB per card on this node)
GPU_UTIL        = 0.90       # vLLM gpu_memory_utilization
HF_DATASET_REPO = "mrlbenchmarks/v1_eval_results"
HF_TOKEN_READ   = os.environ.get("HF_TOKEN_READ", os.environ.get("HF_TOKEN", ""))   # token with access to gated models
HF_TOKEN_WRITE  = os.environ.get("HF_TOKEN_WRITE", os.environ.get("HF_TOKEN", ""))  # token with write access to results repo
TASK_FOR_TYPE   = {
    "instruct": "global_piqa_generation",
    "base":     "global_piqa_cloze",
}
RESULTS_DIR     = Path("./eval_results")
# If your tasks are custom YAML files, set this path; else leave as None
CUSTOM_TASK_DIR = None       # e.g. Path("./custom_tasks")

# ── Model DataFrame ───────────────────────────────────────────────────────────
# Required CSV columns: model_path, type ("instruct" or "base"), large (1 = skip)
# params column is used only for GPU scheduling (how many GPUs to allocate).
# All other columns (family, languages, ...) are ignored.
CSV_PATH = os.environ.get("MODELS_CSV", "models_to_run_small.csv")

def parse_params(val) -> float:
    """Parse '40B' → 40.0, '800M' → 0.8, etc."""
    s = str(val).strip().upper().replace(",", "")
    if s.endswith("B"):  return float(s[:-1])
    if s.endswith("M"):  return float(s[:-1]) / 1000
    return float(s)

def gpus_needed(params_b: float) -> int:
    """How many 80GB GPUs needed to fit model in bfloat16 with headroom."""
    model_gb  = params_b * 2
    usable_gb = VRAM_PER_GPU_GB * GPU_UTIL
    return min(NUM_GPUS, math.ceil(model_gb / usable_gb))

def load_models(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required = {"model_path", "type"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required column(s): {missing}. Found: {list(df.columns)}")

    keep = ["model_path", "type"]
    if "large"  in df.columns: keep.append("large")
    if "params" in df.columns: keep.append("params")
    df = df[keep].copy()

    # Normalize large
    if "large" in df.columns:
        df["large"] = pd.to_numeric(df["large"], errors="coerce").fillna(0).astype(int)
    else:
        df["large"] = 0

    # Parse params → params_b → n_gpus
    if "params" in df.columns:
        df["params_b"] = df["params"].apply(parse_params)
        df["n_gpus"]   = df["params_b"].apply(gpus_needed)
    else:
        df["params_b"] = None
        df["n_gpus"]   = 1

    # Validate and map type → task
    df["type"] = df["type"].str.strip().str.lower()
    unknown = df[~df["type"].isin(TASK_FOR_TYPE)]["type"].unique()
    if len(unknown):
        raise ValueError(f"Unknown type value(s): {unknown}. Expected: {list(TASK_FOR_TYPE)}")
    df["task"] = df["type"].map(TASK_FOR_TYPE)

    print(f"Loaded {len(df)} models from {csv_path}")
    print(f"  instruct → global_piqa_generation : {(df['type']=='instruct').sum()}")
    print(f"  base     → global_piqa_cloze      : {(df['type']=='base').sum()}")
    if "params" in df.columns:
        multi = df[df["n_gpus"] > 1][["model_path", "params_b", "n_gpus"]]
        if not multi.empty:
            print(f"  Multi-GPU models:\n{multi.to_string(index=False)}")
    return df

models_to_run = load_models(CSV_PATH)


# ── GPU helpers ───────────────────────────────────────────────────────────────
# n_gpus is computed per model in load_models() based on params size.
# Models that need more GPUs than available are caught at load time.


# ── GPU pool ──────────────────────────────────────────────────────────────────

class GpuPool:
    """
    Thread-safe GPU slot tracker.
    acquire(n) blocks until n GPUs are free, returns their IDs.
    release(ids) returns GPUs to the pool.
    """
    def __init__(self, num_gpus: int):
        self.free = list(range(num_gpus))
        self._cond = threading.Condition(threading.Lock())

    def acquire(self, n: int) -> list[int]:
        with self._cond:
            while len(self.free) < n:
                self._cond.wait()
            ids, self.free = self.free[:n], self.free[n:]
            return ids

    def release(self, ids: list[int]):
        with self._cond:
            self.free = sorted(self.free + ids)
            self._cond.notify_all()


# ── HF helpers ────────────────────────────────────────────────────────────────

def model_slug(model_path: str) -> str:
    return model_path.replace("/", "__")


def hf_filename(model_path: str) -> str:
    return f"{model_slug(model_path)}__results.json"


def fetch_completed(api: HfApi) -> set:
    """Return set of model_path strings already uploaded to HF."""
    try:
        remote = set(list_repo_files(repo_id=HF_DATASET_REPO, repo_type="dataset", token=HF_TOKEN_WRITE))
    except RepositoryNotFoundError:
        print(f"[WARN] Repo '{HF_DATASET_REPO}' not found — treating as empty.")
        return set()
    except Exception as e:
        print(f"[WARN] HF check failed ({e}) — assuming nothing done yet.")
        return set()

    done = set()
    for mp in models_to_run["model_path"]:
        if hf_filename(mp) in remote:
            done.add(mp)
    return done


def upload(api: HfApi, local_path: Path, model_path: str):
    dest = hf_filename(model_path)
    print(f"  ↑ Uploading {dest} ...")
    try:
        api.upload_file(
            path_or_fileobj=str(local_path),
            path_in_repo=dest,
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            token=HF_TOKEN_WRITE,
            commit_message=f"eval: {model_path}",
        )
        print(f"  ✓ Uploaded {dest}")
    except Exception as e:
        print(f"  [ERROR] Upload failed for {model_path}: {e}")


# ── Eval runner ───────────────────────────────────────────────────────────────

def run_model(model_path: str, task: str, gpu_ids: list[int]) -> Path | None:
    """
    Launch lm_eval (hf backend) for one model + task on the given GPU IDs.
    Single GPU: pins to cuda:0 within the subprocess's CUDA_VISIBLE_DEVICES view.
    Multi-GPU:  uses device_map=auto to shard across all visible GPUs.
    Returns path to result JSON, or None on failure.
    """
    output_dir = RESULTS_DIR / model_slug(model_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    device_map = "cuda:0" if len(gpu_ids) == 1 else "auto"
    model_args = (
        f"pretrained={model_path},max_model_len=8096"
    )

    cmd = [
        "lm_eval",
        "--model", "vllm",
        "--model_args", model_args,
        "--tasks", "global_piqa_generation",
        "--batch_size", "auto",
        "--output_path", str(output_dir),
        "--apply_chat_template",
        "--log_samples",
    ]
    if CUSTOM_TASK_DIR:
        cmd += ["--include_path", str(CUSTOM_TASK_DIR)]

    env = os.environ.copy()
    env["HF_DATASETS_OFFLINE"] = "1"
    env["CUDA_VISIBLE_DEVICES"] = ",".join(str(g) for g in gpu_ids)
    env["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
    if HF_TOKEN_READ:
        env["HF_TOKEN"] = HF_TOKEN_READ

    gpu_str = ",".join(str(g) for g in gpu_ids)
    print(f"\n  ▶ {model_path}  [task={task} | GPU {gpu_str}]")

    proc = subprocess.run(cmd, env=env, text=True, stderr=subprocess.PIPE)

    if proc.returncode != 0:
        print(f"  [ERROR] lm_eval exited {proc.returncode} for {model_path}")
        stderr_tail = "\n".join(proc.stderr.strip().splitlines()[-30:])
        print(f"  [STDERR]\n{stderr_tail}")
        return None

    results = sorted(glob.glob(str(output_dir / "**" / "results_*.json"), recursive=True))
    if not results:
        print(f"  [ERROR] No result JSON found for {model_path}")
        return None

    latest = Path(results[-1])
    print(f"  ■ {model_path} → {latest.name}")
    return latest


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not HF_TOKEN_WRITE:
        raise EnvironmentError("Set HF_TOKEN_WRITE: export HF_TOKEN_WRITE=hf_...")
    if not HF_TOKEN_READ:
        print("[WARN] HF_TOKEN_READ not set — gated models may fail to download")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    api = HfApi(token=HF_TOKEN_WRITE)

    # 1. Drop models flagged as large
    df = models_to_run[models_to_run["large"] != 1].copy()
    print(f"\nModels after large-flag filter: {len(df)}  "
          f"(dropped {len(models_to_run) - len(df)})")

    # 2. Drop models already on HF
    print("\nChecking HF for completed evals...")
    done = fetch_completed(api)
    if done:
        print(f"  Already done ({len(done)}): {sorted(done)}")
    df = df[~df["model_path"].isin(done)].copy()
    print(f"  Remaining: {len(df)} models\n")

    if df.empty:
        print("Nothing to run — all evals already complete!")
        return

    print(f"{'='*60}")
    print(f"Running {len(df)} models across {NUM_GPUS} GPUs\n")

    pool = GpuPool(NUM_GPUS)

    def run_with_gpu(model_path, task, n_gpus):
        """Acquire GPU slots, run eval, release."""
        gpu_ids = pool.acquire(n_gpus)
        try:
            return run_model(model_path, task, gpu_ids)
        finally:
            pool.release(gpu_ids)

    with ThreadPoolExecutor(max_workers=NUM_GPUS) as ex:
        futures = {
            ex.submit(run_with_gpu, row["model_path"], row["task"], int(row["n_gpus"])): row["model_path"]
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
    print("All evals complete.")


if __name__ == "__main__":
    main()
