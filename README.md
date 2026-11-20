# ROYAL BULLS ONE — AI Benchmark Factory

A runnable prototype for the Innodata AI Hackathon Coding Task Factory challenge.

## Demonstrated workflow
1. Generate a reproducible coding task package.
2. Include requirements, a reference implementation and test cases.
3. Execute a candidate solution in-process.
4. Compare outputs and write a JSON evaluation report.
5. View the workflow through a FastAPI web dashboard.

## Current implementation vs roadmap
**Implemented:** deterministic template-based task generation, task manifests, reference files, fixed test cases, candidate evaluation, JSON reports, FastAPI dashboard and API endpoints.

**Planned, not yet implemented:** LLM-generated task diversity, synthetic image generation, multimodal model evaluation, Docker/Harbor isolation, hidden test sets, anti-leakage controls and model-wise benchmarking.

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m benchmark_factory generate --title "Add two numbers" --output data/tasks
python -m benchmark_factory evaluate --task data/tasks/add-two-numbers --candidate examples/candidate_solution.py --output data/reports
uvicorn benchmark_factory.web:app --reload
```

Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs

## Security
This is a hackathon prototype, not a hardened code-execution service. Candidate code currently executes in-process and is **not sandboxed**. Do not evaluate untrusted code or run this service on a sensitive machine. Production deployment must use isolated containers or a dedicated sandbox service with restricted network, filesystem, CPU and memory.

## Reproducibility
Task packages include a manifest, fixed test cases and a reference solution. Reports record task ID/version, candidate, test outcomes, accuracy and timestamp. Scores must be based on actual executions.
