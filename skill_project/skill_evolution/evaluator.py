from __future__ import annotations

from dataclasses import dataclass

from skill_project.skill_evolution.models import (
    ReplayCase,
    ReplayReport,
    ReplayResult,
    SkillCandidate,
)


@dataclass(slots=True)
class HeuristicReplayExecutor:
    """A lightweight executor that simulates using a skill during replay."""

    def run(self, request: str, candidate: SkillCandidate) -> str:
        return (
            f"Request: {request}\n\n"
            f"Applied skill: {candidate.skill_name}\n"
            f"Description: {candidate.description}\n"
            f"When to use: {candidate.when_to_use}\n"
            "Checklist:\n"
            "- Restate the goal and constraints.\n"
            "- Follow the documented procedure.\n"
            "- Check pitfalls before finalizing.\n"
            "- Run verification before returning.\n"
            f"Trigger keywords: {', '.join(candidate.trigger_keywords[:6])}\n"
        )


class ReplayEvaluator:
    def __init__(self, executor: HeuristicReplayExecutor | None = None):
        self.executor = executor or HeuristicReplayExecutor()

    def evaluate(
        self,
        candidate: SkillCandidate,
        cases: list[ReplayCase],
        *,
        min_average_score: float = 0.7,
        min_pass_rate: float = 0.8,
    ) -> ReplayReport:
        if not cases:
            raise ValueError("Replay evaluation requires at least one case.")

        results: list[ReplayResult] = []
        for index, case in enumerate(cases, start=1):
            output = self.executor.run(case.request, candidate)
            results.append(self._score_case(index=index, case=case, output=output))

        average_score = sum(item.score for item in results) / len(results)
        pass_rate = sum(1 for item in results if item.passed) / len(results)
        return ReplayReport(
            candidate_id=candidate.candidate_id,
            average_score=average_score,
            pass_rate=pass_rate,
            min_required_average=min_average_score,
            min_required_pass_rate=min_pass_rate,
            passed=average_score >= min_average_score and pass_rate >= min_pass_rate,
            results=results,
        )

    def _score_case(self, *, index: int, case: ReplayCase, output: str) -> ReplayResult:
        lowered = output.lower()
        matched = [
            keyword for keyword in case.expected_keywords if keyword.lower() in lowered
        ]
        missing = [
            keyword
            for keyword in case.expected_keywords
            if keyword.lower() not in lowered
        ]
        violations = [
            keyword for keyword in case.forbidden_keywords if keyword.lower() in lowered
        ]
        if case.expected_keywords:
            keyword_score = len(matched) / len(case.expected_keywords)
        else:
            keyword_score = 1.0
        penalty = min(len(violations) * 0.25, 1.0)
        score = max(keyword_score - penalty, 0.0)
        return ReplayResult(
            case_id=f"case_{index}",
            request=case.request,
            output=output,
            passed=not missing and not violations,
            score=score,
            matched_keywords=matched,
            missing_keywords=missing,
            violations=violations,
        )
