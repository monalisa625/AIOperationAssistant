from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from .planner import Plan
from tools.github_tool import search_repositories
from tools.weather_tool import get_current_weather


@dataclass
class ExecutorAgent:
    """
    ExecutorAgent iterates through plan steps and calls the corresponding tools.
    It handles retry-once semantics and captures partial failures.
    """

    max_retries_per_step: int = 1

    async def execute_plan(
        self, plan: Plan, only_step_ids: Optional[Iterable[int]] = None
    ) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []

        allowed_ids = set(only_step_ids) if only_step_ids is not None else None

        for step in plan.steps:
            if allowed_ids is not None and step.id not in allowed_ids:
                continue
            tool_name = step.tool
            input_payload = step.input or {}

            step_result: Dict[str, Any] = {
                "step_id": step.id,
                "tool": tool_name,
                "action": step.action,
                "input": input_payload,
            }

            for attempt in range(self.max_retries_per_step + 1):
                try:
                    if tool_name == "github":
                        output = await search_repositories(**input_payload)
                    elif tool_name == "weather":
                        output = await get_current_weather(**input_payload)
                    else:
                        output = {
                            "error": f"Unknown tool '{tool_name}'",
                        }

                    step_result["output"] = output
                    step_result["success"] = "error" not in output
                    break
                except Exception as exc:  # pragma: no cover - defensive
                    step_result["output"] = {"error": str(exc)}
                    step_result["success"] = False
                    if attempt >= self.max_retries_per_step:
                        break

            results.append(step_result)

        return {"steps": results}

