import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone

def evaluate_candidate(task_dir: Path, candidate_file: Path, output_dir: Path) -> Path:
    """Evaluate a trusted candidate file in-process; this is not a security sandbox."""
    task_dir = task_dir.resolve()
    candidate_file = candidate_file.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    cases = json.loads((task_dir / manifest["tests_file"]).read_text(encoding="utf-8"))
    results = []
    status = "completed"
    error = ""
    try:
        spec = importlib.util.spec_from_file_location("candidate_solution", candidate_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load candidate file: {candidate_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for case in cases:
            try:
                actual = module.add_numbers(*case["input"])
                results.append({
                    "passed": actual == case["expected"],
                    "expected": case["expected"],
                    "actual": actual
                })
            except Exception as exc:
                results.append({"passed": False, "error": type(exc).__name__ + ": " + str(exc)})
    except Exception as exc:
        status = "runtime_error"
        error = type(exc).__name__ + ": " + str(exc)
    passed = sum(1 for item in results if item.get("passed"))
    total = len(cases)
    report_data = {
        "task_id": manifest["task_id"],
        "task_version": manifest["version"],
        "candidate": candidate_file.name,
        "status": status,
        "passed": passed,
        "total": total,
        "accuracy": round(passed / total, 4) if total else 0,
        "results": results,
        "error": error,
        "execution_mode": "in_process_prototype_not_sandboxed",
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }
    report_path = output_dir / f"{manifest['task_id']}-report.json"
    report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    return report_path
