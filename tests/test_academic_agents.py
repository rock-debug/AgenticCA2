"""
Comprehensive Test Suite for Academic Research Assistant Multi-Agent System
Covers the required scenarios and structural contracts:
1. Plain Python Tool Functions & Semantic Kernel Plugin Contract (>= 2 real tools per agent)
2. Scenario 1: Grounded Literature Synthesis, Per-Claim Passage Mapping & Multi-Agent Trace
3. Scenario 2: Critic Failure Handling (Detecting & Pruning Unsupported / Hallucinated Claims)
4. Scenario 3: Contradiction Detection & Dual-Perspective Dossier
"""

import inspect
import pytest
from app.agents.orchestrator import AcademicPipelineOrchestrator
from app.agents.tools import (
    decompose_research_question,
    expand_academic_lexicon,
    search_paper_passages,
    filter_and_rank_passages,
    cluster_passages_by_themes,
    draft_themed_synthesis,
    extract_atomic_claims,
    audit_claim_entailment,
    detect_cross_source_divergence,
    synthesize_contradiction_dossier,
    filter_unsupported_claims,
    compile_grounded_report,
    QueryAgentTools,
    RetrievalAgentTools,
    SummaryAgentTools,
    FactCheckAgentTools,
    ContradictionAgentTools,
    WriterAgentTools
)


@pytest.fixture
def orchestrator():
    """Initializes the multi-agent pipeline orchestrator built on Semantic Kernel."""
    return AcademicPipelineOrchestrator()


def test_plain_python_tools_contract(orchestrator):
    """
    Tool Contract: Each working agent calls at least two real tools written as plain Python functions.
    Verifies that all 12 tools exist as standalone plain Python functions and are registered in Semantic Kernel.
    """
    plain_functions = [
        decompose_research_question,
        expand_academic_lexicon,
        search_paper_passages,
        filter_and_rank_passages,
        cluster_passages_by_themes,
        draft_themed_synthesis,
        extract_atomic_claims,
        audit_claim_entailment,
        detect_cross_source_divergence,
        synthesize_contradiction_dossier,
        filter_unsupported_claims,
        compile_grounded_report,
    ]
    for fn in plain_functions:
        assert inspect.isfunction(fn), f"{fn} must be a plain Python function"

    # Also verify Semantic Kernel plugin registration across all 6 agents
    expected_plugins = [
        "QueryPlugin",
        "RetrievalPlugin",
        "SummaryPlugin",
        "FactCheckPlugin",
        "ContradictionPlugin",
        "WriterPlugin",
    ]
    for plugin_name in expected_plugins:
        assert plugin_name in orchestrator.kernel.plugins


def test_scenario_1_grounded_pipeline_execution(orchestrator):
    """
    SCENARIO 1: Standard Grounded Research Pipeline Run.
    Verifies:
    - All 6 modular agents execute in pipeline sequence.
    - Themed literature summary is generated.
    - Every retained claim maps to a retrieved passage citation tag [P1..Pn].
    - Unsupported synthesis extrapolations are dropped and listed in dropped_claims.
    - Timestamped 12-step multi-agent execution trace is populated.
    """
    question = "How does the Transformer self-attention mechanism overcome recurrence limitations?"
    result = orchestrator.run_pipeline(question=question)

    assert result["run_id"].startswith("RUN-")
    assert len(result["agents_executed"]) == 6
    assert len(result["sub_queries"]) >= 2
    assert len(result["passages"]) > 0
    assert len(result["retained_claims"]) >= 4
    assert len(result["dropped_claims"]) >= 1
    assert "final_report" in result
    assert "markdown_report" in result["final_report"]

    retrieved_tags = {p["citation_tag"] for p in result["passages"]}
    for claim in result["retained_claims"]:
        assert claim["cited_tag"] in retrieved_tags
        assert claim["status"] == "SUPPORTED"

    # Verify trace contains all 6 agents and 12 tool invocations (2 tools per agent)
    assert len(result["agent_trace"]) == 12
    agent_names_in_trace = {step["agent"] for step in result["agent_trace"]}
    assert agent_names_in_trace == {
        "Query Agent",
        "Retrieval Agent",
        "Summary Agent",
        "Fact-Check Agent (Critic)",
        "Contradiction Agent",
        "Writer Agent",
    }


def test_scenario_2_critic_catches_and_prunes_hallucinations(orchestrator):
    """
    SCENARIO 2: Critic Failure Handling & Hallucination Pruning.
    Verifies:
    - Injected ungrounded assertion ([P99]) and speculative extrapolations are flagged
      as UNSUPPORTED by the Fact-Check Critic Agent.
    - Writer Agent isolates and prunes unsupported claims into 'dropped_claims'.
    - Pruned claims do NOT appear in retained_claims or the themed summary sections.
    """
    question = "What are the empirical trade-offs of residual networks?"
    result = orchestrator.run_pipeline(question=question, inject_unsupported_claim=True)

    dropped = result["dropped_claims"]
    assert len(dropped) >= 2

    injected_flags = [
        d for d in dropped
        if "INJECTED" in d.get("claim_id", "") or "Quantum" in d.get("statement", "")
    ]
    assert len(injected_flags) == 1
    assert injected_flags[0]["status"] == "UNSUPPORTED"
    assert "FAIL" in injected_flags[0]["critic_verdict"]

    retained_texts = [c["statement"] for c in result["retained_claims"]]
    for text in retained_texts:
        assert "Quantum optical processors" not in text
        assert "Neuromorphic photonic" not in text


def test_scenario_3_contradiction_detection_dual_perspective(orchestrator):
    """
    SCENARIO 3: Contradiction Detection & Balanced Dossier.
    Verifies:
    - Pipeline detects conflicting academic positions across retrieved literature.
    - Contradiction Agent articulates Position A vs Position B with source grounding.
    - Final Markdown report includes both opposing positions.
    """
    question = "Compare centralized orchestration vs decentralized blackboard architectures for autonomous agent systems."
    result = orchestrator.run_pipeline(question=question)

    contradictions = result["contradictions"]
    assert contradictions.get("has_contradictions") is True
    assert len(contradictions.get("dossiers", [])) >= 1

    dossier = contradictions["dossiers"][0]
    assert "position_a" in dossier and "position_b" in dossier
    assert "Chen" in dossier["position_a"]["source"]
    assert "Weber" in dossier["position_b"]["source"]
    assert "Position A" in result["final_report"]["markdown_report"]
    assert "Position B" in result["final_report"]["markdown_report"]
