# Ask Benchmark AI — Chat-First Product Specification

## Product direction
The primary user experience is a single conversational interface. Users describe benchmark work in natural language; the assistant asks only essential follow-up questions and invokes backend actions when supported.

## Current milestone (v0.2)
- Chat-first responsive home page.
- POST /api/chat endpoint with input validation and deterministic intent routing.
- Existing task generation and evaluation actions exposed through chat.
- Results are returned from actual backend execution, not fabricated.
- Existing /api/tasks, /api/reports and /docs endpoints remain available.
- Explicit disclosure that this prototype is not yet LLM-powered and candidate execution is not sandboxed.

## Current capability boundary
- Generator currently produces one fixed Python add_numbers task.
- Evaluator currently runs the bundled trusted example candidate only.
- Candidate code executes in-process; never expose this endpoint to untrusted candidate code.
- Chat routing is rule-based. No model provider/API key is configured.

## Target user journey
1. User describes a coding benchmark request in chat.
2. Assistant identifies missing requirements and asks one focused question at a time.
3. Assistant creates a versioned task package with requirements, reference solution and test cases.
4. User supplies a candidate solution through a future controlled upload flow.
5. An isolated execution worker runs tests and records reproducible results.
6. Assistant summarizes the measured score and links the report.

## Next engineering milestones
1. Replace fixed template with a configurable task schema: title, language, difficulty, prompt, entrypoint, input/output contract and test cases.
2. Add LLM provider adapter with explicit environment-based configuration; never hardcode API keys.
3. Add secure isolated execution (container or dedicated sandbox), resource limits, timeout and restricted network.
4. Add hidden test sets, versioning, rubric-based scoring and anti-leakage controls.
5. Add persisted conversation/task sessions and report downloads.
6. Add deployment, health checks, observability and demo evidence.

## Acceptance criteria
- Chat is the default landing page on desktop and mobile.
- User messages are validated and bounded.
- Generate/evaluate actions call existing backend functions.
- The UI shows returned backend results and handles API errors.
- No response claims an LLM, sandbox, arbitrary language support or task capability that is not implemented.
