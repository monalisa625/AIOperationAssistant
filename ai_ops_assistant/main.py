import argparse
import asyncio
import os
from typing import Any, Dict

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from dotenv import load_dotenv
load_dotenv()





async def run_task(task: str) -> Dict[str, Any]:
    """
    Run the full multi-agent pipeline for a given natural language task.
    """
    planner = PlannerAgent()
    executor = ExecutorAgent()
    verifier = VerifierAgent()

    # 1) Planning
    plan = await planner.create_plan(task)

    # 2) First execution pass
    execution_result = await executor.execute_plan(plan)

    # 3) Verification pass – the verifier can request re-execution
    verification = await verifier.analyze(task, plan, execution_result)

    if verification.status == "retry" and verification.retry_step_ids:
        # Re-run only the requested steps, then verify once more.
        retry_ids = verification.retry_step_ids
        retry_execution = await executor.execute_plan(plan, only_step_ids=retry_ids)

        # Merge the retried step outputs back into the original execution log.
        original_steps = {s["step_id"]: s for s in execution_result.get("steps", [])}
        for s in retry_execution.get("steps", []):
            original_steps[s["step_id"]] = s

        execution_result = {"steps": list(original_steps.values())}
        verification = await verifier.analyze(task, plan, execution_result)

    final_output = verifier.build_final_payload(task, plan, execution_result, verification)
    return final_output


def run_cli() -> None:
    """
    Simple CLI entrypoint.
    Usage:
        python main.py "Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London."
    """
    parser = argparse.ArgumentParser(description="AI Operations Assistant")
    parser.add_argument("task", type=str, help="Natural language task to run")
    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="Run as CLI or start FastAPI server",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for FastAPI server (when --mode api)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Port for FastAPI server (when --mode api)",
    )

    args = parser.parse_args()
    # Note: load_dotenv() is already called at module level (line 10)
    # and also in llm/client.py before client initialization

    if args.mode == "api":
        # Defer FastAPI import so CLI users don't pay the import cost unless needed.
        import uvicorn  # type: ignore
        from fastapi import FastAPI
        from pydantic import BaseModel

        app = FastAPI(title="AI Operations Assistant")

        class RunRequest(BaseModel):
            task: str

        @app.post("/run")
        async def run_endpoint(request: RunRequest) -> Dict[str, Any]:
            return await run_task(request.task)

        uvicorn.run(app, host=args.host, port=args.port)
    else:
        # CLI mode: run the full pipeline and print the final JSON.
        final_output = asyncio.run(run_task(args.task))
        # Pretty-print as JSON for readability.
        import json

        print(json.dumps(final_output, indent=2))


if __name__ == "__main__":
    run_cli()

