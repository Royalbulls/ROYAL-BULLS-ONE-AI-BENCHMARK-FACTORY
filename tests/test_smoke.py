import json
from pathlib import Path
from benchmark_factory.generator import generate_task
from benchmark_factory.runner import evaluate_candidate

def test_generate_and_evaluate(tmp_path):
    task = generate_task("Add two numbers", tmp_path / "tasks")
    candidate = Path(__file__).parents[1] / "examples" / "candidate_solution.py"
    report = evaluate_candidate(task, candidate, tmp_path / "reports")
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["status"] == "completed"
    assert data["passed"] == 4
    assert data["total"] == 4
    assert data["accuracy"] == 1.0
