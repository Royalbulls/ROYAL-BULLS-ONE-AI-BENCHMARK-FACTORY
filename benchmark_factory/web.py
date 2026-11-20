import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .generator import generate_task
from .runner import evaluate_candidate

app = FastAPI(title="ROYAL BULLS ONE — Ask Benchmark AI", version="0.2.0")
BASE = Path.cwd()
TASKS, REPORTS = BASE / "data/tasks", BASE / "data/reports"
EXAMPLE = BASE / "examples/candidate_solution.py"


class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(min_length=16, max_length=80)


CHAT_PAGE = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ask Benchmark AI | ROYAL BULLS ONE</title>
<style>
:root{color-scheme:light;--ink:#17243a;--muted:#64748b;--line:#e2e8f0;--blue:#2459a6;--bg:#f5f7fb}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,Arial,sans-serif}
header{background:#10233f;color:#fff;padding:17px max(20px,calc((100% - 900px)/2));display:flex;align-items:center;gap:12px}
.logo{width:40px;height:40px;border-radius:12px;background:#2459a6;display:grid;place-items:center;font-weight:800}
.brand{font-weight:750;letter-spacing:.02em}.sub{font-size:12px;color:#cbd5e1}
main{max-width:900px;margin:24px auto;padding:0 16px;display:flex;flex-direction:column;min-height:calc(100vh - 90px)}
.intro{padding:18px 4px 12px}.intro h1{font-size:25px;margin:0 0 5px}.intro p{margin:0;color:var(--muted)}
#chat{flex:1;display:flex;flex-direction:column;gap:14px;padding:12px 0 20px}
.msg{max-width:85%;padding:13px 16px;border-radius:17px;white-space:pre-wrap;overflow-wrap:anywhere}
.bot{background:#fff;border:1px solid var(--line);align-self:flex-start;border-bottom-left-radius:5px}
.user{background:var(--blue);color:#fff;align-self:flex-end;border-bottom-right-radius:5px}
.meta{font-size:11px;color:var(--muted);margin-top:6px}.user .meta{color:#dbeafe}
.composer{position:sticky;bottom:0;background:var(--bg);padding:12px 0 18px}
form{display:flex;gap:9px;background:#fff;border:1px solid #cbd5e1;border-radius:18px;padding:8px;box-shadow:0 8px 30px #17243a0d}
textarea{border:0;outline:0;resize:none;flex:1;min-height:42px;max-height:130px;padding:10px;font:inherit}
button{border:0;border-radius:13px;background:var(--blue);color:white;padding:0 19px;font-weight:700;cursor:pointer}
button:disabled{opacity:.55;cursor:wait}.hint{font-size:12px;color:var(--muted);text-align:center;margin:8px}
.links{display:flex;gap:14px;justify-content:center;font-size:12px;margin:6px}.links a{color:var(--blue)}
@media(max-width:600px){main{margin:10px auto;min-height:calc(100vh - 75px)}.intro h1{font-size:22px}.msg{max-width:94%}header{padding:12px 16px}}
</style>
</head>
<body>
<header><div class="logo">RB</div><div><div class="brand">ROYAL BULLS ONE</div><div class="sub">Ask Benchmark AI · Coding Task Factory</div></div></header>
<main>
<section class="intro"><h1>Ask your Benchmark Expert</h1><p>Describe what you need. Get guided help with coding tasks and evaluation.</p></section>
<section id="chat" aria-live="polite">
<div class="msg bot">Hello! I’m Ask Benchmark AI. I can help create coding benchmark tasks, explain test cases and evaluate a trusted Python candidate using the current prototype.\n\nWhat would you like to do?</div>
</section>
<div class="composer"><form id="form"><textarea id="message" rows="1" placeholder="Ask anything about coding benchmarks..." aria-label="Your message" required></textarea><button id="send" type="submit">Send</button></form><div class="hint">Enter to send · Shift + Enter for a new line</div><div class="links"><a href="/api/tasks">Tasks</a><a href="/api/reports">Reports</a><a href="/docs">API documentation</a></div></div>
</main>
<script>
const chat=document.getElementById('chat'),form=document.getElementById('form'),input=document.getElementById('message'),send=document.getElementById('send');\nconst sessionId=sessionStorage.getItem('rbo_benchmark_session')||('rbo_'+crypto.randomUUID());sessionStorage.setItem('rbo_benchmark_session',sessionId);
function add(text,kind){const node=document.createElement('div');node.className='msg '+kind;node.textContent=text;chat.appendChild(node);node.scrollIntoView({behavior:'smooth',block:'end'});return node}
form.addEventListener('submit',async e=>{e.preventDefault();const message=input.value.trim();if(!message)return;add(message,'user');input.value='';send.disabled=true;send.textContent='...';const pending=add('Thinking through your request...','bot');try{const response=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,session_id:sessionId})});const data=await response.json();if(!response.ok)throw new Error(data.detail||'Request failed');pending.textContent=data.reply;if(data.result)pending.textContent+='\n\nBackend result:\n'+JSON.stringify(data.result,null,2)}catch(err){pending.textContent='I could not complete that request: '+err.message+' Please try again.'}finally{send.disabled=false;send.textContent='Send';input.focus()}});
input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();form.requestSubmit()}});
</script>
</body></html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(CHAT_PAGE)


@app.post("/api/chat")
def chat(message: ChatMessage):
    from .ai_assistant import get_assistant_reply, AssistantConfigurationError

    text = message.message.strip()
    normalized = text.lower()

    # Real OpenAI Responses API conversation; fail clearly if credentials are not configured.
    try:
        reply = get_assistant_reply(message.session_id, text)
    except AssistantConfigurationError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=502, detail=f"AI provider request failed: {type(exc).__name__}") from exc

    # The assistant can explain and guide freely. Only deterministic backend actions
    # below are allowed to claim task creation or evaluation has actually happened.
    if not any(word in normalized for word in ("evaluate", "evaluation", "run test", "test my", "check code", "score", "generate", "create", "make", "banao", "बनाओ", "तैयार")):
        return {"reply": reply}

    if any(word in normalized for word in ("evaluate", "evaluation", "run test", "test my", "check code", "score")):
        task = TASKS / "add-two-numbers"
        if not (task / "task.json").exists():
            generate_task("Add two numbers", TASKS)
        report = evaluate_candidate(task, EXAMPLE, REPORTS)
        result = json.loads(report.read_text(encoding="utf-8"))
        return {
            "reply": reply + "\\n\\nEvaluation completed for the bundled trusted example candidate. "
                "The current prototype supports this fixed Python add_numbers task only. "
                "It does not yet accept arbitrary uploaded code or run untrusted code safely."
            ),
            "result": result,
        }

    if any(word in normalized for word in ("generate", "create", "make", "banao", "बनाओ", "तैयार")) and any(word in normalized for word in ("task", "benchmark", "coding", "कोड", "टास्क")):
        path = generate_task("Add two numbers", TASKS)
        manifest = json.loads((path / "task.json").read_text(encoding="utf-8"))
        return {
            "reply": reply + "\\n\\nA sample coding task package has been generated successfully. "
                "This first version currently generates the fixed Python add_numbers exercise; "
                "custom problem generation and difficulty selection are planned next."
            ),
            "result": {
                "task_id": manifest["task_id"],
                "language": manifest["language"],
                "task_path": str(path),
                "test_case_count": len(json.loads((path / manifest["tests_file"]).read_text(encoding="utf-8"))),
            },
        }

    return {
        "reply": (
            "I can guide you through the current Coding Task Factory prototype. "
            "Right now it can generate one fixed Python addition task and evaluate the bundled trusted example. "
            "It is not yet connected to an LLM, so this chat uses rule-based routing rather than open-ended AI reasoning. "
            "Would you like me to generate the sample task or run its evaluation?"
        )
    }


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
