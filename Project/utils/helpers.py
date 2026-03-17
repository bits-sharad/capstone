from __future__ import annotations

from typing import Dict, List, Tuple, Any

from Project.state import AgentResult


def calculate_overall_score(results: Dict[str, AgentResult]) -> float:
    if not results:
        return 0.0
    return sum(r.get("score", 0.0) for r in results.values()) / len(results)


def merge_issues(results: Dict[str, AgentResult]) -> List[str]:
    merged: List[str] = []
    for r in results.values():
        merged.extend(r.get("issues", []))
    # Deduplicate while preserving order
    seen = set()
    unique: List[str] = []
    for item in merged:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def merge_recommendations(results: Dict[str, AgentResult]) -> List[str]:
    merged: List[str] = []
    for r in results.values():
        merged.extend(r.get("suggestions", []))
    seen = set()
    unique: List[str] = []
    for item in merged:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def count_check_statuses(results: Dict[str, AgentResult]) -> Dict[str, int]:
    counts = {"passed": 0, "warning": 0, "failed": 0}
    for r in results.values():
        status = r.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def determine_final_status(overall_score: float, critical_issues: List[str]) -> str:
    if critical_issues or overall_score < 60:
        return "rejected"
    if overall_score < 80:
        return "needs_review"
    return "approved"


def extract_critical_issues(results: Dict[str, AgentResult]) -> List[str]:
    critical: List[str] = []
    for name, r in results.items():
        if r.get("status") == "failed":
            issues = r.get("issues") or [f"{name} check failed."]
            critical.extend(issues)
    return critical

