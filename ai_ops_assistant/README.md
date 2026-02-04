## AI Operations Assistant

Production-style, local, multi-agent **AI Operations Assistant** for a GenAI internship assignment.  
The assistant accepts a natural-language task, plans tool calls, executes them against real third-party APIs, and verifies the results before returning a final structured answer.

### Architecture Overview

- **Planner Agent** (`PlannerAgent`):
  - Uses the LLM with a strict JSON-only prompt.
  - Converts a user task into an ordered list of steps.
  - Each step specifies:
    - `id` – numeric step id
    - `action` – human-readable description
    - `tool` – `github` or `weather`
    - `input` – JSON payload passed to the tool

- **Executor Agent** (`ExecutorAgent`):
  - Iterates through plan steps and calls real tools.
  - Tools:
    - `github_tool.search_repositories` – GitHub REST API
    - `weather_tool.get_current_weather` – OpenWeatherMap (or compatible) API
  - Handles:
    - Retry-once semantics for each step
    - Partial failures and error capture

- **Verifier Agent** (`VerifierAgent`):
  - Uses the LLM with a different prompt from the planner.
  - Checks for:
    - Missing data
    - Empty or erroneous API responses
    - Structural issues in the results
  - Can request specific step re-execution (by id); the main orchestrator re-runs only those steps and calls the verifier again.
  - Produces a final, structured JSON payload.

### ASCII Architecture Diagram

```text
          +------------------+
          |   CLI / API      |
          |   (main.py)      |
          +---------+--------+
                    |
                    v
          +------------------+
          |  Planner Agent   |
          | (LLM, JSON plan) |
          +---------+--------+
                    |
                    v
          +------------------+
          |  Executor Agent  |
          |  (tool invoker)  |
          +----+--------+----+
               |        |
       GitHub tool   Weather tool
     (github_tool)  (weather_tool)
               |        |
               v        v
          +------------------+
          |  Verifier Agent  |
          | (LLM, checks &   |
          |  final output)   |
          +------------------+
```

### How Agents Work Together

1. **Planner** receives the raw user task and produces a strict JSON plan:
   - Uses `PLANNER_SYSTEM_PROMPT` + `PLANNER_USER_TEMPLATE`.
   - Output is validated with Pydantic models (`Plan`, `PlanStep`).
2. **Executor** takes the validated plan:
   - Executes each step in order, calling the requested tool.
   - Each step is wrapped in retry-once logic.
   - Collects raw outputs into a list of step results.
3. **Verifier** receives the task, plan, and execution results:
   - Uses `VERIFIER_SYSTEM_PROMPT` + `VERIFIER_USER_TEMPLATE`.
   - Returns a `VerificationResult` describing:
     - `status` (`ok` or `retry`)
     - `retry_step_ids` to re-run (if needed)
     - Per-step health and issues
     - A final user-facing summary and a machine-friendly `structured_output`.
4. **Orchestrator (main)**:
   - Runs Planner → Executor → Verifier.
   - If `status == "retry"` and `retry_step_ids` is non-empty:
     - Re-runs only those steps via `ExecutorAgent.execute_plan(..., only_step_ids=...)`.
     - Merges updated results and calls the Verifier again.
   - Returns the Verifier’s final structured payload.

### Project Structure

```text
ai_ops_assistant/
│
├── agents/
│   ├── planner.py      # PlannerAgent + Plan models
│   ├── executor.py     # ExecutorAgent with retry and partial failure handling
│   ├── verifier.py     # VerifierAgent using LLM for checks and final output
│   └── __init__.py
│
├── tools/
│   ├── github_tool.py  # GitHub REST API integration
│   ├── weather_tool.py # OpenWeatherMap (or compatible) integration
│   └── __init__.py
│
├── llm/
│   ├── client.py       # Centralized OpenAI Async client
│   ├── prompts.py      # Planner & Verifier prompt templates
│   └── __init__.py
│
├── main.py             # CLI & FastAPI entrypoints, orchestration
├── requirements.txt
├── .env.example
└── README.md
```

### Setup Instructions

1. **Clone / copy the project**

   Place the `ai_ops_assistant` folder in your working directory.

2. **Create and activate a virtual environment (recommended)**

```bash
python -m venv .venv
.venv\Scripts\activate  # on Windows
# or
source .venv/bin/activate  # on macOS/Linux
```

3. **Install dependencies**

```bash
cd ai_ops_assistant
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Required / optional variables:

- **OPENAI_API_KEY** – required, for LLM calls.
- **OPENAI_MODEL** – optional, defaults to `gpt-4.1-mini`.
- **GITHUB_TOKEN** – optional, increases GitHub rate limits.
- **OPENWEATHER_API_KEY** – required, from OpenWeatherMap (or compatible).

### Runtime Options

You can run the assistant either via **CLI** or **FastAPI**.

#### CLI Usage

From the `ai_ops_assistant` directory:

```bash
python main.py "Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London."
```

This will:

- Plan the task.
- Call GitHub and weather APIs.
- Verify the results.
- Print a final JSON payload to the terminal.

Example (truncated) output shape:

```json
{
  "task": "Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London.",
  "plan": {
    "steps": [
      {
        "id": 1,
        "action": "search_github",
        "tool": "github",
        "input": { "query": "AI agents", "per_page": 3 }
      },
      {
        "id": 2,
        "action": "get_weather",
        "tool": "weather",
        "input": { "city": "London", "units": "metric" }
      }
    ]
  },
  "execution": {
    "steps": [
      {
        "step_id": 1,
        "tool": "github",
        "action": "search_github",
        "input": { "query": "AI agents", "per_page": 3 },
        "success": true,
        "output": {
          "query": "AI agents",
          "total_count": 12345,
          "items": [
            { "full_name": "...", "stargazers_count": 1234, "description": "..." }
          ]
        }
      },
      {
        "step_id": 2,
        "tool": "weather",
        "action": "get_weather",
        "input": { "city": "London", "units": "metric" },
        "success": true,
        "output": {
          "city": "London",
          "temperature": 19.2,
          "description": "light rain"
        }
      }
    ]
  },
  "verification": {
    "status": "ok",
    "retry_step_ids": [],
    "summary": "Here are 3 popular AI agent GitHub repos and the current weather in London...",
    "structured_output": {
      "github": { "repositories": [ /* ... */ ] },
      "weather": { "city": "London", "temperature": 19.2, "description": "light rain" }
    },
    "steps": [
      { "step_id": 1, "ok": true, "issues": [] },
      { "step_id": 2, "ok": true, "issues": [] }
    ]
  }
}
```

#### FastAPI Usage

Start the API server:

```bash
python main.py "ignored-in-api-mode" --mode api --host 0.0.0.0 --port 8000
```

Then call the endpoint:

```bash
curl -X POST "http://localhost:8000/run" ^
  -H "Content-Type: application/json" ^
  -d "{\"task\": \"Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London.\"}"
```

The response body matches the JSON shape described above.

### Notes on Error Handling

- **Planner errors**:
  - Planner output is parsed as JSON and validated with Pydantic.
  - On JSON/validation errors, the planner retries a few times before raising.
- **Executor errors**:
  - Each tool call is wrapped with retry-once semantics.
  - Network / HTTP issues are captured as:
    - `{"error": "..."}` inside the `output` field.
  - `success` is set to `False` when an error is present.
- **Weather tool**:
  - If `OPENWEATHER_API_KEY` is missing, the tool returns a structured error object instead of throwing.
- **Verifier errors**:
  - The verifier expects strict JSON; if the LLM returns invalid JSON, the code falls back to a simple `VerificationResult` that wraps the raw text in `structured_output.raw`.
  - The verifier can set `status: "retry"` and list `retry_step_ids`; the orchestrator will re-run those steps once and call the verifier again.

### Example Task Supported

> **“Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London.”**

- Planner typically produces:
  - Step 1 – `tool: "github"`, `input: {"query": "AI agents", "per_page": 3}`
  - Step 2 – `tool: "weather"`, `input: {"city": "London", "units": "metric"}`
- Executor:
  - Calls GitHub’s search API and OpenWeatherMap’s current weather API.
- Verifier:
  - Confirms both steps returned non-empty, well-formed data.
  - Builds a final JSON response combining both results.

### Improvements with More Time

- **Richer toolset**:
  - Add more operational tools (e.g., incident management, logging, metrics).
- **Persistent memory / state**:
  - Store past runs and allow the planner to re-use previous results.
- **Better observability**:
  - Structured logging, trace IDs, and per-step timing metrics.
- **Configurable planning policies**:
  - Allow users to specify constraints (max tools, latency budgets, etc.).
- **Streaming responses**:
  - Stream partial verification summaries back to the CLI / API client.
- **Advanced verification**:
  - Cross-check multiple APIs or perform sanity checks against historical norms.

