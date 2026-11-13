"""
Query Agent Module (CSE476 - Group 16: Academic Research Assistant Team)
Role: Turns the user's research question into targeted search sub-queries
over the provided academic paper set.
"""

import time
from typing import Dict, Any, List, Optional
from app.agents.tools import (
    QueryAgentTools,
    decompose_research_question,
    expand_academic_lexicon
)


class QueryAgent:
    """
    QueryAgent:
    Specialized agent module responsible for decomposing raw user research questions
    into multi-faceted academic search sub-queries and expanding domain terminology.
    Calls two plain Python tool functions registered with Microsoft Semantic Kernel.
    """

    def __init__(self, kernel=None):
        self.agent_name = "Query Agent"
        self.plugin_name = "QueryPlugin"
        self.role = "Query Decomposition & Academic Lexicon Expansion"
        self.tools = QueryAgentTools()
        self.kernel = kernel

    def execute(
        self,
        question: str,
        trace: Optional[List[Dict[str, Any]]] = None,
        shared_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes query decomposition and lexicon expansion using two plain Python tools.
        """
        start_time = time.time()

        # Tool 1 (Plain Python Function): decompose_research_question
        t1_start = time.time()
        sub_queries = decompose_research_question(question)
        t1_duration = round((time.time() - t1_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "decompose_research_question",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": question,
                "output": sub_queries,
                "duration_ms": t1_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        # Tool 2 (Plain Python Function): expand_academic_lexicon
        t2_start = time.time()
        expanded_queries = expand_academic_lexicon(sub_queries)
        t2_duration = round((time.time() - t2_start) * 1000, 2)

        if trace is not None:
            trace.append({
                "agent": self.agent_name,
                "tool": "expand_academic_lexicon",
                "tool_type": "Plain Python Function / Semantic Kernel @kernel_function",
                "input": sub_queries,
                "output": expanded_queries,
                "duration_ms": t2_duration,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        total_duration = round((time.time() - start_time) * 1000, 2)
        output = {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "original_question": question,
            "sub_queries": sub_queries,
            "expanded_queries": expanded_queries,
            "duration_ms": total_duration
        }

        if shared_state is not None:
            shared_state["question"] = question
            shared_state["sub_queries"] = sub_queries
            shared_state["expanded_queries"] = expanded_queries

        return output
