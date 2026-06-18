from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Literal
from .schemas import AttemptTrace, QAExample, ReflectionEntry, RunRecord

# Switch between mock and real LLM via env var AGENT_MODE=mock|llm (default: llm)
_MODE = os.getenv("AGENT_MODE", "llm")

if _MODE == "mock":
    from .mock_runtime import FAILURE_MODE_BY_QID
    from .mock_runtime import actor_answer as _mock_actor
    from .mock_runtime import evaluator as _mock_evaluator
    from .mock_runtime import reflector as _mock_reflector

    def _actor(example, attempt_id, agent_type, reflection_memory):
        return _mock_actor(example, attempt_id, agent_type, reflection_memory), 0, 0

    def _evaluator(example, answer):
        return _mock_evaluator(example, answer), 0, 0

    def _reflector(example, attempt_id, judge):
        return _mock_reflector(example, attempt_id, judge), 0, 0

    def _failure_mode(qid, final_score):
        return "none" if final_score == 1 else FAILURE_MODE_BY_QID.get(qid, "wrong_final_answer")

else:
    from .llm_runtime import actor_answer as _actor  # type: ignore[assignment]
    from .llm_runtime import evaluator as _evaluator  # type: ignore[assignment]
    from .llm_runtime import reflector as _reflector  # type: ignore[assignment]

    def _failure_mode(qid, final_score):
        return "none" if final_score == 1 else "wrong_final_answer"


@dataclass
class BaseAgent:
    agent_type: Literal["react", "reflexion"]
    max_attempts: int = 1

    def run(self, example: QAExample) -> RunRecord:
        reflection_memory: list[str] = []
        reflections: list[ReflectionEntry] = []
        traces: list[AttemptTrace] = []
        final_answer = ""
        final_score = 0

        for attempt_id in range(1, self.max_attempts + 1):
            answer, actor_tokens, actor_latency = _actor(example, attempt_id, self.agent_type, reflection_memory)
            judge, eval_tokens, eval_latency = _evaluator(example, answer)

            token_estimate = actor_tokens + eval_tokens
            latency_ms = actor_latency + eval_latency

            trace = AttemptTrace(
                attempt_id=attempt_id,
                answer=answer,
                score=judge.score,
                reason=judge.reason,
                token_estimate=token_estimate,
                latency_ms=latency_ms,
            )
            final_answer = answer
            final_score = judge.score

            if judge.score == 1:
                traces.append(trace)
                break

            if self.agent_type == "reflexion" and attempt_id < self.max_attempts:
                reflection, ref_tokens, ref_latency = _reflector(example, attempt_id, judge)
                reflections.append(reflection)
                reflection_memory.append(reflection.next_strategy)
                trace.reflection = reflection
                trace.token_estimate += ref_tokens
                trace.latency_ms += ref_latency

            traces.append(trace)

        total_tokens = sum(t.token_estimate for t in traces)
        total_latency = sum(t.latency_ms for t in traces)
        failure_mode = _failure_mode(example.qid, final_score)

        return RunRecord(
            qid=example.qid,
            question=example.question,
            gold_answer=example.gold_answer,
            agent_type=self.agent_type,
            predicted_answer=final_answer,
            is_correct=bool(final_score),
            attempts=len(traces),
            token_estimate=total_tokens,
            latency_ms=total_latency,
            failure_mode=failure_mode,
            reflections=reflections,
            traces=traces,
        )


class ReActAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="react", max_attempts=1)


class ReflexionAgent(BaseAgent):
    def __init__(self, max_attempts: int = 3) -> None:
        super().__init__(agent_type="reflexion", max_attempts=max_attempts)
