"""
Contradiction Agent Module
Role: Reports where two sources disagree and presents both positions in a structured dossier.
"""

import time
from typing import Dict, Any, List, Optional
from app.agents.tools import (
    ContradictionAgentTools,
    detect_cross_source_divergence,
    synthesize_contradiction_dossier
)


class ContradictionAgent:
    """
    ContradictionAgent:
    Specialized agent module responsible for detecting empirical disagreements, conflicting
    paradigms, and methodological debates across retrieved sources, formatting them
    into a balanced, dual-perspective dossier.
    Calls two plain Python tool functions registered with Microsoft Semantic Kernel.
    """

    def __init__(self, kernel=None):
        self.agent_name = "Contradiction Agent"
        self.plugin_name = "ContradictionPlugin"
        self.role = "Cross-Source Divergence & Multi-Perspective Synthesis"
        self.tools = ContradictionAgentTools()
        self.kernel = kernel

    def execute(
        self,
        passages: List[Dict[str, Any]],
        claims: Optional[List[Dict[str, Any]]] = None,
        trace: Optional[List[Dict[str, Any]]] = None,
        shared_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes cross-source divergence detection and dossier synthesis using two plain Python tools.
        """
        start_time = time.time()

        # Tool 1 (Plain Python Function): detect_cross_source_divergence
        t1_start = time.time()
        divergences = detect_cross_source_divergence(passages=passages)
        t1_duration = round((time.time() - t1_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "detect_cross_source_divergence",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"passages_analyzed": len(passages)},
                "output": {"divergent_debates_found": len(divergences)},
                "duration_ms": t1_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        # Tool 2 (Plain Python Function): synthesize_contradiction_dossier
        t2_start = time.time()
        dossier = synthesize_contradiction_dossier(divergences=divergences)
        t2_duration = round((time.time() - t2_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "synthesize_contradiction_dossier",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"divergences_count": len(divergences)},
                "output": {
                    "has_contradictions": dossier.get("has_contradictions"),
                    "dossiers": [d["topic"] for d in dossier.get("dossiers", [])]
                },
                "duration_ms": t2_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        total_duration = round((time.time() - start_time) * 1000, 2)
        output = {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "has_contradictions": dossier.get("has_contradictions", False),
            "contradiction_dossier": dossier,
            "duration_ms": total_duration
        }

        if shared_state is not None:
            shared_state["contradictions"] = dossier

        return output
