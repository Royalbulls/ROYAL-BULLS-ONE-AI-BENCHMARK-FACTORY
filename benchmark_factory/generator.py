import json
import re
from pathlib import Path
from datetime import datetime, timezone

def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "benchmark-task"

def generate_task(title: str, output_dir: Path) -> Path:
    task_id = slugify(title)
    task_dir = output_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "task_id": task_id, "version": "1.0.0", "title": title,
        "domain": "coding", "language": "python",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requirements": [
            "Implement a function named add_numbers(a, b).",
            "Return the numeric sum of the two inputs.",
            "Support integers and floating-point values."
        ],
        "reference_file": "reference_solution.py",
        "candidate_entrypoint": "solution.py",
        "tests_file": "test_cases.json",
        "expected_behavior": "add_numbers(a, b) returns a + b."
    }
    tests = [
        {"input": [2, 3], "expected": 5},
        {"input": [-4, 9], "expected": 5},
        {"input": [1.5, 2.25], "expected": 3.75},
        {"input": [0, 0], "expected": 0}
    ]
    reference = "def add_numbers(a, b):\n    return a + b\n"
    (task_dir / "task.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (task_dir / "test_cases.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")
    (task_dir / "reference_solution.py").write_text(reference, encoding="utf-8")
    return task_dir
