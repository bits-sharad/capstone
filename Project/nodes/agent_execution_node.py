"""
Agent Execution Node - Executes all quality checking agents
"""

from __future__ import annotations

from typing import Optional

from Project.state import ProductQualityState
from Project.analyzer.quality_analyzer import QualityAnalyzer


def agent_execution_node(
    state: ProductQualityState, analyzer: Optional[QualityAnalyzer] = None
) -> ProductQualityState:
    state["current_step"] = "agent_execution"  # type: ignore[index]

    # Skip if validation already rejected the product
    if state.get("final_status") == "rejected":
        return state

    if analyzer is None:
        errors = list(state.get("errors", []))
        errors.append("QualityAnalyzer instance is required for agent execution.")
        state["errors"] = errors  # type: ignore[index]
        return state

    product = state.get("product", {})

    try:
        results = analyzer.run_all_checks(product)
        quality_results = dict(state.get("quality_results", {}))
        quality_results.update(results)
        state["quality_results"] = quality_results  # type: ignore[index]

        metadata = state.get("metadata") or {}
        total_checks = len(results)
        stats = metadata.get("stats") or {}
        stats["total_checks"] = total_checks
        metadata["stats"] = stats
        state["metadata"] = metadata  # type: ignore[index]
    except Exception as exc:
        errors = list(state.get("errors", []))
        errors.append(f"Error executing agents: {exc}")
        state["errors"] = errors  # type: ignore[index]

    return state

