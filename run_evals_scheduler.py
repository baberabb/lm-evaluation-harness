"""
Scheduler-based eval runner (alternative to run_evals.py).

Pipes one lm_eval shell command per model into `simple_gpu_scheduler`, which
assigns each command to its own GPU via CUDA_VISIBLE_DEVICES. Each command
also calls back into this script with --upload once lm_eval succeeds, so
results are uploaded to HF as jobs finish (crash-safe).

Multi-GPU models (anything whose params don't fit on one GPU) are skipped.

Usage:
    pip install lm_eval vllm huggingface_hub pandas simple-gpu-scheduler
    python run_evals_scheduler.py                   # uses MODELS_CSV or default
    MODELS_CSV=/path/to/other.csv python run_evals_scheduler.py
    DRY_RUN=1 python run_evals_scheduler.py         # print commands, don't run
    python run_evals_scheduler.py --upload <model>  # upload a single result
"""

import glob
import os
import shlex
import subprocess
import sys
from pathlib import Path

from huggingface_hub import HfApi

from run_evals import (
    CSV_PATH,
    CUSTOM_TASK_DIR,
    HF_TOKEN_READ,
    HF_TOKEN_WRITE,
    NUM_GPUS,
    RESULTS_DIR,
    fetch_completed,
    load_models,
    model_slug,
    upload,
)

SCHEDULER_BIN = "simple_gpu_scheduler"
SCRIPT_PATH = Path(__file__).resolve()


def build_eval_command(model_path: str, task: str) -> str:
    """
    Build a single shell command that runs lm_eval for one model and, on
    success, re-invokes this script to upload the result. CUDA_VISIBLE_DEVICES
    is set by simple_gpu_scheduler, not here.
    """
    output_dir = RESULTS_DIR / model_slug(model_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_args = f"pretrained={model_path},max_model_len=8096"

    env_parts = [
        "HF_DATASETS_OFFLINE=1",
        "PYTORCH_ALLOC_CONF=expandable_segments:True",
    ]
    if HF_TOKEN_READ:
        env_parts.append(f"HF_TOKEN={shlex.quote(HF_TOKEN_READ)}")
    if HF_TOKEN_WRITE:
        env_parts.append(f"HF_TOKEN_WRITE={shlex.quote(HF_TOKEN_WRITE)}")

    lm_eval_argv = [
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
        lm_eval_argv += ["--include_path", str(CUSTOM_TASK_DIR)]

    eval_part = " ".join(shlex.quote(a) for a in lm_eval_argv)
    upload_part = " ".join(
        shlex.quote(a) for a in [sys.executable, str(SCRIPT_PATH), "--upload", model_path]
    )

    return f"{' '.join(env_parts)} {eval_part} && {upload_part}"


def upload_one(model_path: str) -> int:
    """Find the newest result JSON for this model and upload it to HF."""
    slug = model_slug(model_path)
    pattern = str(RESULTS_DIR / slug / "**" / "results_*.json")
    results = sorted(glob.glob(pattern, recursive=True))
    if not results:
        print(f"[ERROR] No result JSON found for {model_path} under {RESULTS_DIR / slug}")
        return 1

    api = HfApi(token=HF_TOKEN_WRITE)
    upload(api, Path(results[-1]), model_path)
    return 0


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--upload":
        return upload_one(sys.argv[2])

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

    # 3. Drop multi-GPU models — simple_gpu_scheduler runs one job per GPU.
    multi = df[df["n_gpus"] > 1]
    if not multi.empty:
        print(f"\nSkipping {len(multi)} multi-GPU models "
              f"(simple_gpu_scheduler is 1 GPU per job):")
        for _, row in multi.iterrows():
            print(f"  - {row['model_path']}  ({row.get('params_b', '?')}B, needs {row['n_gpus']} GPUs)")
    df = df[df["n_gpus"] == 1].copy()

    if df.empty:
        print("\nNothing to run.")
        return 0

    commands = [build_eval_command(row["model_path"], row["task"]) for _, row in df.iterrows()]

    print(f"\n{'='*60}")
    print(f"Running {len(commands)} models across {NUM_GPUS} GPUs via {SCHEDULER_BIN}\n")

    if os.environ.get("DRY_RUN"):
        print("DRY_RUN=1 — printing commands instead of running:\n")
        for cmd in commands:
            print(cmd)
        return 0

    scheduler_cmd = [SCHEDULER_BIN, "--gpus", *[str(g) for g in range(NUM_GPUS)]]
    proc = subprocess.Popen(scheduler_cmd, stdin=subprocess.PIPE, text=True)
    assert proc.stdin is not None
    for cmd in commands:
        proc.stdin.write(cmd + "\n")
    proc.stdin.close()
    rc = proc.wait()

    print(f"\n{'='*60}")
    print(f"Scheduler exited with code {rc}.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
