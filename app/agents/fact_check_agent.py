"""
Fact-Check Agent Module (CSE476 - Group 16: Academic Research Assistant Team)
Role: The CRITIC Agent in the Pipeline with RAG and Critic Architecture.
Verifies each claim in the summary against retrieved passages and flags unsupported ones.
"""

import time
from typing import Dict, Any, List, Optional
from app.agents.tools import (
    FactCheckAgentTools,
    extract_atomic_claims,
    audit_claim_entailment
)


class FactCheckAgent:
    """
    FactCheckAgent (The Critic):
    Specialized critic agent module that extracts atomic proposition claims from
    draft summaries, evaluates entailment against grounded retrieved passages,
    calculates verification confidence, and flags unsupported assertions.
    Calls two plain Python tool functions registered with Microsoft Semantic Kernel.
    """

    def __init__(self, kernel=None):
        self.agent_name = "Fact-Check Agent (Critic)"
        self.plugin_name = "FactCheckPlugin"
        self.role = "NLI Claim Entailment Audit & Hallucination Gate"
        self.tools = FactCheckAgentTools()
        self.kernel = kernel

    def execute(
        self,
        candidate_claims: List[Dict[str, Any]],
        passages: List[Dict[str, Any]],
        trace: Optional[List[Dict[str, Any]]] = None,
        shared_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes atomic claim extraction and entailment audit using two plain Python tools.
        """
        start_time = time.time()

        # Tool 1 (Plain Python Function): extract_atomic_claims
        t1_start = time.time()
        atomic_claims = extract_atomic_claims(candidate_claims)
        t1_duration = round((time.time() - t1_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "extract_atomic_claims",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"candidate_claims_count": len(candidate_claims)},
                "output": {"atomic_claims_extracted": len(atomic_claims)},
                "duration_ms": t1_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        # Tool 2 (Plain Python Function): audit_claim_entailment
        t2_start = time.time()
        audited_claims = audit_claim_entailment(atomic_claims, passages)
        t2_duration = round((time.time() - t2_start) * 1000, 2)

        supported_count = sum(1 for c in audited_claims if c.get("status") == "SUPPORTED")
        unsupported_count = len(audited_claims) - supported_count

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "audit_claim_entailment",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"claims_to_audit": len(atomic_claims), "passages_in_memory": len(passages)},
                "output": {
                    "supported": supported_count,
                    "unsupported_flagged": unsupported_count,
                    "verdicts": [
                        {"claim": c["claim_id"], "status": c["status"], "score": c["confidence"]}
                        for c in audited_claims
                    ]
                },
                "duration_ms": t2_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        total_duration = round((time.time() - start_time) * 1000, 2)
        output = {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "audited_claims": audited_claims,
            "supported_count": supported_count,
            "unsupported_count": unsupported_count,
            "duration_ms": total_duration
        }

        if shared_state is not None:
            shared_state["audited_claims"] = audited_claims

        return output
