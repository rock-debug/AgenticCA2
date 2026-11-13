"""
Writer Agent Module (CSE476 - Group 16: Academic Research Assistant Team)
Role: Produces the final summary keeping only supported claims, with sources,
plus an explicit list of any claims dropped as unsupported.
"""

import time
from typing import Dict, Any, List, Optional
from app.agents.tools import (
    WriterAgentTools,
    filter_unsupported_claims,
    compile_grounded_report
)


class WriterAgent:
    """
    WriterAgent:
    Specialized agent module responsible for enforcing zero tolerance for hallucinations:
    filters out unsupported claims flagged by the Fact-Check Critic, maps every retained
    claim to its grounded passage citation, and compiles the final themed literature review.
    Calls two plain Python tool functions registered with Microsoft Semantic Kernel.
    """

    def __init__(self, kernel=None):
        self.agent_name = "Writer Agent"
        self.plugin_name = "WriterPlugin"
        self.role = "Report Compilation, Citation Grounding & Hallucination Pruning"
        self.tools = WriterAgentTools()
        self.kernel = kernel

    def execute(
        self,
        audited_claims: List[Dict[str, Any]],
        passages: List[Dict[str, Any]],
        contradiction_dossier: Dict[str, Any],
        question: str,
        trace: Optional[List[Dict[str, Any]]] = None,
        shared_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes claim filtering and report assembly using two plain Python tools.
        """
        start_time = time.time()

        # Tool 1 (Plain Python Function): filter_unsupported_claims
        t1_start = time.time()
        filtered = filter_unsupported_claims(audited_claims=audited_claims)
        retained = filtered.get("retained_claims", [])
        dropped = filtered.get("dropped_claims", [])
        t1_duration = round((time.time() - t1_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "filter_unsupported_claims",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"total_claims_reviewed": len(audited_claims)},
                "output": {"retained_count": len(retained), "dropped_count": len(dropped)},
                "duration_ms": t1_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        # Tool 2 (Plain Python Function): compile_grounded_report
        t2_start = time.time()
        report = compile_grounded_report(
            retained_claims=retained,
            dropped_claims=dropped,
            contradictions=contradiction_dossier or {},
            sources=passages,
            question=question
        )
        t2_duration = round((time.time() - t2_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "compile_grounded_report",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"retained_claims_count": len(retained), "sources_count": len(passages)},
                "output": {
                    "report_title": report.get("title"),
                    "retained_assertions": len(retained),
                    "dropped_assertions": len(dropped),
                    "markdown_length_chars": len(report.get("markdown_report", ""))
                },
                "duration_ms": t2_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        total_duration = round((time.time() - start_time) * 1000, 2)
        output = {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "report": report,
            "retained_claims": retained,
            "dropped_claims": dropped,
            "duration_ms": total_duration
        }

        if shared_state is not None:
            shared_state["retained_claims"] = retained
            shared_state["dropped_claims"] = dropped
            shared_state["final_report"] = report

        return output
