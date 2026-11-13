"""
Retrieval Agent Module (CSE476 - Group 16: Academic Research Assistant Team)
Role: Fetches the relevant passages (RAG) for each sub-query over the paper document set.
"""

import time
from typing import Dict, Any, List, Optional
from app.agents.tools import (
    RetrievalAgentTools,
    search_paper_passages,
    filter_and_rank_passages
)


class RetrievalAgent:
    """
    RetrievalAgent:
    Specialized agent module responsible for executing grounded RAG over the provided
    paper corpus, scoring relevance, deduplicating passages, and assigning citation keys [P1..Pn].
    Calls two plain Python tool functions registered with Microsoft Semantic Kernel.
    """

    def __init__(self, kernel=None):
        self.agent_name = "Retrieval Agent"
        self.plugin_name = "RetrievalPlugin"
        self.role = "Corpus RAG & Passage Scoring"
        self.tools = RetrievalAgentTools()
        self.kernel = kernel

    def execute(
        self,
        sub_queries: List[str],
        custom_passages: Optional[List[Dict[str, Any]]] = None,
        trace: Optional[List[Dict[str, Any]]] = None,
        shared_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes grounded RAG search and passage filtering using two plain Python tools.
        """
        start_time = time.time()

        # Tool 1 (Plain Python Function): search_paper_passages
        t1_start = time.time()
        raw_passages = search_paper_passages(
            sub_queries=sub_queries,
            top_k=6,
            custom_passages=custom_passages
        )
        t1_duration = round((time.time() - t1_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "search_paper_passages",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"sub_queries_count": len(sub_queries)},
                "output": {"raw_passages_found": len(raw_passages)},
                "duration_ms": t1_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        # Tool 2 (Plain Python Function): filter_and_rank_passages
        t2_start = time.time()
        ranked_passages = filter_and_rank_passages(
            passages=raw_passages,
            min_score=0.03,
            max_results=6
        )
        t2_duration = round((time.time() - t2_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "filter_and_rank_passages",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": {"raw_candidates": len(raw_passages)},
                "output": {
                    "ranked_passages": [
                        f"{p.get('citation_tag')}: {p.get('paper_title')} ({p.get('section')})"
                        for p in ranked_passages
                    ]
                },
                "duration_ms": t2_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        total_duration = round((time.time() - start_time) * 1000, 2)
        output = {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "passages_count": len(ranked_passages),
            "passages": ranked_passages,
            "duration_ms": total_duration
        }

        if shared_state is not None:
            shared_state["passages"] = ranked_passages

        return output
