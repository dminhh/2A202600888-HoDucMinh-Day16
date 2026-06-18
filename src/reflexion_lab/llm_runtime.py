from __future__ import annotations
import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM
from .schemas import JudgeResult, QAExample, ReflectionEntry

load_dotenv()
_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _chat(system: str, user: str) -> tuple[str, int, int]:
    """Returns (content, total_tokens, latency_ms)."""
    t0 = time.monotonic()
    resp = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0,
    )
    latency_ms = int((time.monotonic() - t0) * 1000)
    content = resp.choices[0].message.content or ""
    tokens = resp.usage.total_tokens if resp.usage else 0
    return content, tokens, latency_ms


def actor_answer(
    example: QAExample,
    attempt_id: int,
    agent_type: str,
    reflection_memory: list[str],
) -> tuple[str, int, int]:
    context_text = "\n\n".join(
        f"[{c.title}]\n{c.text}" for c in example.context
    )
    reflection_section = ""
    if reflection_memory:
        notes = "\n".join(f"- {r}" for r in reflection_memory)
        reflection_section = f"\n\nReflection notes from previous attempts:\n{notes}"

    user_msg = (
        f"Question: {example.question}\n\n"
        f"Context:\n{context_text}"
        f"{reflection_section}\n\n"
        f"Answer:"
    )
    content, tokens, latency = _chat(ACTOR_SYSTEM, user_msg)
    return content.strip(), tokens, latency


def evaluator(example: QAExample, answer: str) -> tuple[JudgeResult, int, int]:
    user_msg = (
        f"Question: {example.question}\n"
        f"Gold answer: {example.gold_answer}\n"
        f"Predicted answer: {answer}"
    )
    content, tokens, latency = _chat(EVALUATOR_SYSTEM, user_msg)
    try:
        # strip markdown code fences if present
        text = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(text)
    except Exception:
        data = {"score": 0, "reason": f"Parse error: {content}", "missing_evidence": [], "spurious_claims": []}
    return JudgeResult(**data), tokens, latency


def reflector(
    example: QAExample, attempt_id: int, judge: JudgeResult
) -> tuple[ReflectionEntry, int, int]:
    user_msg = (
        f"Question: {example.question}\n"
        f"Wrong answer given: (see evaluator reason)\n"
        f"Evaluator reason: {judge.reason}\n"
        f"Missing evidence: {judge.missing_evidence}\n"
        f"Spurious claims: {judge.spurious_claims}"
    )
    content, tokens, latency = _chat(REFLECTOR_SYSTEM, user_msg)
    try:
        text = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(text)
    except Exception:
        data = {
            "failure_reason": judge.reason,
            "lesson": "Re-read the context carefully.",
            "next_strategy": "Trace each hop explicitly before giving the final answer.",
        }
    return ReflectionEntry(attempt_id=attempt_id, **data), tokens, latency
