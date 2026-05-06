"""
Vibecoding Bench - Evaluation Runner

跑一个或多个评测任务在指定模型上，结果保存到 results/<model>/<task>__run<N>.json。

Usage:
    python run_eval.py --task 03 --model claude-sonnet-4-5 --runs 3
    python run_eval.py --task all --model mimo-v2.5 --runs 3 \
        --output ../results/mimo-v2.5/
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from models import ModelClient, get_client

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"
RESULTS_DIR = ROOT / "results"


def load_task(task_id: str) -> dict[str, Any]:
    """Load a single task definition by id prefix (e.g. '03')."""
    matches = [d for d in TASKS_DIR.iterdir() if d.is_dir() and d.name.startswith(f"{task_id}-")]
    if not matches:
        raise FileNotFoundError(f"Task {task_id} not found under {TASKS_DIR}")
    task_dir = matches[0]
    return {
        "id": task_dir.name,
        "task": (task_dir / "task.md").read_text(encoding="utf-8"),
        "expected": (task_dir / "expected.md").read_text(encoding="utf-8"),
        "rubric": json.loads((task_dir / "rubric.json").read_text(encoding="utf-8")),
        "repo_path": task_dir / "repo",
    }


def snapshot_repo(repo_path: Path, max_chars: int = 80_000) -> str:
    """Pack a repo into a single text blob (truncated for context budget)."""
    if not repo_path.exists():
        return "(no repo provided)"

    SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".lock", ".bin", ".woff", ".woff2"}
    SKIP_DIR = {"node_modules", ".git", "dist", "build", ".next", "__pycache__"}

    chunks: list[str] = []
    used = 0
    for f in sorted(repo_path.rglob("*")):
        if not f.is_file() or f.suffix in SKIP_SUFFIX:
            continue
        if any(part in SKIP_DIR for part in f.parts):
            continue
        try:
            body = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = f.relative_to(repo_path)
        block = f"\n\n=== FILE: {rel} ===\n{body}"
        if used + len(block) > max_chars:
            chunks.append(f"\n\n[... truncated at {max_chars} chars ...]")
            break
        chunks.append(block)
        used += len(block)
    return "".join(chunks)


def build_prompt(task: dict, repo_snapshot: str) -> str:
    repo_section = (
        f"\n\n## 项目代码快照\n```\n{repo_snapshot}\n```\n" if repo_snapshot.strip() else ""
    )
    return (
        "你是一个资深软件工程师，请完成下面的真实开发任务。\n"
        "请按任务描述里的输出格式给出完整代码与决策说明。\n"
        "\n---\n\n"
        f"{task['task']}"
        f"{repo_section}"
        "\n请开始。"
    )


def run_single(task: dict, model: ModelClient, run_idx: int) -> dict:
    """Run one (task, model, run_idx) trial."""
    repo_text = snapshot_repo(task["repo_path"])
    prompt = build_prompt(task, repo_text)

    t0 = time.time()
    error: str | None = None
    response = ""
    try:
        response = model.complete(prompt)
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    elapsed = round(time.time() - t0, 2)

    return {
        "task_id": task["id"],
        "model": model.name,
        "run": run_idx,
        "elapsed_s": elapsed,
        "input_tokens": getattr(model, "last_input_tokens", None),
        "output_tokens": getattr(model, "last_output_tokens", None),
        "prompt_chars": len(prompt),
        "response": response,
        "error": error,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def discover_task_ids() -> list[str]:
    return sorted({d.name.split("-", 1)[0] for d in TASKS_DIR.iterdir() if d.is_dir()})


def main() -> None:
    parser = argparse.ArgumentParser(description="Vibecoding Bench evaluation runner")
    parser.add_argument("--task", required=True, help="Task id prefix (e.g. '03') or 'all'")
    parser.add_argument("--model", required=True, help="Registered model name (see models.py)")
    parser.add_argument("--runs", type=int, default=3, help="Repeat each task N times")
    parser.add_argument("--output", default=None, help="Output dir (default: results/<model>/)")
    args = parser.parse_args()

    task_ids = discover_task_ids() if args.task == "all" else [args.task]
    model = get_client(args.model)

    out_dir = Path(args.output) if args.output else RESULTS_DIR / args.model
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[Vibecoding Bench] model={model.name} tasks={task_ids} runs={args.runs}")
    print(f"  output -> {out_dir}\n")

    for tid in task_ids:
        task = load_task(tid)
        print(f">>> Task {task['id']}")
        for i in range(args.runs):
            print(f"    run {i + 1}/{args.runs} ... ", end="", flush=True)
            result = run_single(task, model, i + 1)
            out_file = out_dir / f"{task['id']}__run{i + 1}.json"
            out_file.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            status = "ERR" if result["error"] else "OK"
            print(f"{status} ({result['elapsed_s']}s, in={result['input_tokens']}, out={result['output_tokens']})")

    print(f"\nDone. Results: {out_dir}")


if __name__ == "__main__":
    main()
