from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from pydantic import BaseModel, Field, ValidationError

from llm.client import llm_client
from llm.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE


class PlanStep(BaseModel):
    id: int = Field(..., description="Monotonic step id starting from 1.")
    action: str = Field(..., description="Natural language description of the step.")
    tool: str = Field(
        ...,
        description="The tool identifier to use, e.g. 'github' or 'weather'.",
    )
    input: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON input payload passed to the tool.",
    )


class Plan(BaseModel):
    steps: List[PlanStep] = Field(
        default_factory=list,
        description="Ordered list of execution steps.",
    )


@dataclass
class PlannerAgent:
    """
    PlannerAgent uses the LLM to convert a natural language task into
    a deterministic JSON execution plan.
    """

    max_retries: int = 2

    async def create_plan(self, task: str) -> Plan:
        """
        Ask the LLM to create a plan and validate it against the Plan schema.
        Retries a few times if the model returns invalid JSON.
        """
        for attempt in range(self.max_retries + 1):
            response_text = await llm_client.complete_json(
                system_prompt=PLANNER_SYSTEM_PROMPT,
                user_prompt=PLANNER_USER_TEMPLATE.format(task=task),
            )
            try:
                data = json.loads(response_text)
                plan = Plan.model_validate(data)
                return plan
            except (json.JSONDecodeError, ValidationError):
                if attempt >= self.max_retries:
                    raise
        # This is unreachable but keeps type-checkers happy.
        return Plan(steps=[])

