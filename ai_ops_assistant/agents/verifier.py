from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from pydantic import BaseModel, Field, ValidationError

from llm.client import llm_client
from llm.prompts import VERIFIER_SYSTEM_PROMPT, VERIFIER_USER_TEMPLATE


class VerifiedStep(BaseModel):
    step_id: int
    ok: bool
    issues: List[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    status: str = Field(
        ...,
        description="Either 'ok' or 'retry'.",
    )
    retry_step_ids: List[int] = Field(
        default_factory=list, description="Steps that should be re-executed if needed."
    )
    summary: str = Field(
        ...,
        description="Natural language summary for the user.",
    )
    structured_output: Dict[str, Any] = Field(
        default_factory=dict,
        description="Machine-friendly final result.",
    )
    steps: List[VerifiedStep] = Field(default_factory=list)


@dataclass
class VerifierAgent:
    """
    VerifierAgent inspects raw execution results using an LLM and produces
    a final structured answer. It can also request specific steps to be
    re-run if they appear to be missing or invalid.
    """

    async def analyze(
        self, task: str, plan: Any, execution_result: Dict[str, Any]
    ) -> VerificationResult:
        user_prompt = VERIFIER_USER_TEMPLATE.format(
            task=task,
            plan_json=json.dumps(plan.model_dump(), indent=2),
            execution_json=json.dumps(execution_result, indent=2),
        )
        response_text = await llm_client.complete_json(
            system_prompt=VERIFIER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        data = json.loads(response_text)
        try:
            return VerificationResult.model_validate(data)
        except ValidationError:
            # Fallback: wrap raw text in a minimal structure.
            return VerificationResult(
                status="ok",
                retry_step_ids=[],
                summary="Verifier returned un-parseable JSON; falling back to raw text.",
                structured_output={"raw": response_text},
                steps=[],
            )

    def build_final_payload(
        self,
        task: str,
        plan: Any,
        execution_result: Dict[str, Any],
        verification: VerificationResult,
    ) -> Dict[str, Any]:
        """
        Build the final structured output returned to the caller.
        """
        return {
            "task": task,
            "plan": plan.model_dump(),
            "execution": execution_result,
            "verification": verification.model_dump(),
        }


