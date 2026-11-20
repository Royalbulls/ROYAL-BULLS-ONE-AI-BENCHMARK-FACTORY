# Architecture

```text
Feature specification
        |
        v
Task generator ---> task.json + test_cases.json + reference_solution.py
        |
        v
Evaluation runner -> in-process candidate execution
        |
        v
Result parser ----> JSON report
        |
        v
FastAPI dashboard -> task list / report list / API docs
```

Implemented: deterministic template task generator, in-process candidate evaluator, JSON report storage and FastAPI dashboard.

Planned: LLM task-generation adapter, synthetic image tasks, multimodal evaluator, Docker/Harbor sandbox workers, hidden tests, anti-leakage controls and model comparison.
