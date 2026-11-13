"""
Summary Agent Module (CSE476 - Group 16: Academic Research Assistant Team)
Role: Writes a structured summary grouped by theme from retrieved passages.
"""

import time
from typing import Dict, Any, List, Optional
from app.agents.tools import (
    SummaryAgentTools,
    cluster_passages_by_themes,
    draft_themed_synthesis
)


class SummaryAgent:
    """
    SummaryAgent:
    Specialized agent module responsible for categorizing retrieved passages into
    thematic clusters and drafting an initial multi-theme synthesis with per-claim source tags.
    Calls two plain Python tool functions registered with Microsoft Semantic Kernel.
    """

    def __init__(self, kernel=None):
        self.agent_name = "Summary Agent"
        self.plugin_name = "SummaryPlugin"
        self.role = "Thematic Clustering & Structured Synthesis Drafting"
        self.tools = SummaryAgentTools()
        self.kernel = kernel

    def execute(
        self,
        question: str,
        passages: List[Dict[str, Any]],
        trace: Optional[List[Dict[str, Any]]] = None,
        shared_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes thematic clustering and draft synthesis using two plain Python tools.
        """
        start_time = time.time()

        # Tool 1 (Plain Python Function): cluster_passages_by_themes
        t1_start = time.time()
        themes = cluster_passages_by_themes(passages)
        t1_duration = round((time.time() - t1_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "cluster_passages_by_themes",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"passages_count": len(passages)},
                "output": {"identified_themes": list(themes.keys())},
                "duration_ms": t1_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        # Tool 2 (Plain Python Function): draft_themed_synthesis
        t2_start = time.time()
        synthesis = draft_themed_synthesis(themes=themes, question=question)
        t2_duration = round((time.time() - t2_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "draft_themed_synthesis",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"themes_count": len(themes)},
                "output": {
                    "candidate_claims_count": len(synthesis.get("candidate_claims", [])),
                    "themes_generated": [t["theme"] for t in synthesis.get("themes", [])]
                },
                "duration_ms": t2_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        total_duration = round((time.time() - start_time) * 1000, 2)
        output = {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "themes": synthesis.get("themes", []),
            "candidate_claims": synthesis.get("candidate_claims", []),
            "duration_ms": total_duration
        }

        if shared_state is not None:
            shared_state["draft_themes"] = synthesis.get("themes", [])
            shared_state["candidate_claims"] = synthesis.get("candidate_claims", [])

        return output
