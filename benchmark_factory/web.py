import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .generator import generate_task
from .runner import evaluate_candidate

app = FastAPI(title="ROYAL BULLS ONE — AI Benchmark Factory", version="0.1.0")
BASE = Path.cwd()
TASKS, REPORTS = BASE / "data/tasks", BASE / "data/reports"
EXAMPLE = BASE / "examples/candidate_solution.py"

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ROYAL BULLS ONE Benchmark Factory</title><style>
body{font-family:Arial,sans-serif;background:#f3f6fb;color:#17243a;margin:0}
header{background:#10233f;color:white;padding:24px 6%}main{max-width:900px;margin:28px auto;padding:0 18px}
.card{background:white;border:1px solid #dce4ef;border-radius:14px;padding:20px;margin:14px 0}
button{background:#2459a6;color:white;border:0;border-radius:8px;padding:12px 18px;font-weight:bold;cursor:pointer}
a{color:#2459a6}</style></head><body><header><h1>ROYAL BULLS ONE</h1>AI Benchmark Factory · Coding Task Factory</header>
<main><section class="card"><h2>Generate benchmark task</h2><p>Create a versioned task manifest, reference implementation and test cases.</p>
<form method="post" action="/generate"><button>Generate sample task</button></form></section>
<section class="card"><h2>Evaluate candidate</h2><p>Run the included example candidate against the generated task.</p>
<form method="post" action="/evaluate"><button>Run evaluation</button></form></section>
<section class="card"><h2>Inspect results</h2><p><a href="/api/tasks">Task manifests</a> · <a href="/api/reports">Evaluation reports</a> · <a href="/docs">Interactive API docs</a></p>
<p>Prototype warning: candidate code executes in-process and is not sandboxed. Use trusted code only.</p></section></main></body></html>""")

@app.post("/generate")
def generate():
    path = generate_task("Add two numbers", TASKS)
    return {"message": "Task generated", "task_path": str(path)}

@app.post("/evaluate")
def evaluate():
    task = TASKS / "add-two-numbers"
    if not (task / "task.json").exists():
        generate_task("Add two numbers", TASKS)
    report = evaluate_candidate(task, EXAMPLE, REPORTS)
    return json.loads(report.read_text(encoding="utf-8"))

@app.get("/api/tasks")
def list_tasks():
    return [json.loads(p.read_text(encoding="utf-8")) for p in TASKS.glob("*/task.json")] if TASKS.exists() else []

@app.get("/api/reports")
def list_reports():
    return [json.loads(p.read_text(encoding="utf-8")) for p in REPORTS.glob("*.json")] if REPORTS.exists() else []
