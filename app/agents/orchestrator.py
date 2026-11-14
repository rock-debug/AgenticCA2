"""
Academic Research Assistant Orchestrator
Architecture: Pipeline with RAG and a Critic Architecture.
Framework: Microsoft Semantic Kernel (Python).
Coordinates 6 specialized modular agents over shared pipeline state with append-only run logging.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from app.agents.tools import (
    QueryAgentTools,
    RetrievalAgentTools,
    SummaryAgentTools,
    FactCheckAgentTools,
    ContradictionAgentTools,
    WriterAgentTools
)
from app.agents.query_agent import QueryAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.summary_agent import SummaryAgent
from app.agents.fact_check_agent import FactCheckAgent
from app.agents.contradiction_agent import ContradictionAgent
from app.agents.writer_agent import WriterAgent
from app.agents.corpus import get_paper_passages

logger = logging.getLogger(__name__)

RUN_LOG_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "..", "..", "run_log.jsonl"
)


class AcademicPipelineOrchestrator:
    """
    AcademicPipelineOrchestrator:
    Coordinates the 6-agent pipeline with RAG and Critic architecture.
    Registers all tool plugins into Semantic Kernel, maintains a shared state object
    across all agents, and appends execution traces to run_log.jsonl.
    """

    def __init__(self, api_key: str = None, model_id: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.model_id = model_id or os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

        # Initialize Microsoft Semantic Kernel
        self.kernel = Kernel()
        self._init_semantic_kernel()

        # Initialize the 6 specialized agent modules
        self.query_agent = QueryAgent(kernel=self.kernel)
        self.retrieval_agent = RetrievalAgent(kernel=self.kernel)
        self.summary_agent = SummaryAgent(kernel=self.kernel)
        self.fact_check_agent = FactCheckAgent(kernel=self.kernel)
        self.contradiction_agent = ContradictionAgent(kernel=self.kernel)
        self.writer_agent = WriterAgent(kernel=self.kernel)

    def _init_semantic_kernel(self):
        """Registers agent tool plugins and AI services in Semantic Kernel."""
        try:
            self.kernel.add_plugin(QueryAgentTools(), plugin_name="QueryPlugin")
            self.kernel.add_plugin(RetrievalAgentTools(), plugin_name="RetrievalPlugin")
            self.kernel.add_plugin(SummaryAgentTools(), plugin_name="SummaryPlugin")
            self.kernel.add_plugin(FactCheckAgentTools(), plugin_name="FactCheckPlugin")
            self.kernel.add_plugin(ContradictionAgentTools(), plugin_name="ContradictionPlugin")
            self.kernel.add_plugin(WriterAgentTools(), plugin_name="WriterPlugin")

            if self.api_key and self.api_key != "your_groq_api_key_here":
                async_client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                chat_service = OpenAIChatCompletion(
                    ai_model_id=self.model_id,
                    service_id="academic_chat_service",
                    async_client=async_client
                )
                self.kernel.add_service(chat_service)
        except Exception as e:
            logger.warning(f"Semantic Kernel optional LLM service binding notice: {e}")

    def run_pipeline(
        self,
        question: str,
        custom_corpus: Optional[List[Dict[str, Any]]] = None,
        inject_unsupported_claim: bool = False
    ) -> Dict[str, Any]:
        """
        Executes the full multi-agent pipeline:
        1. QueryAgent -> decomposes research inquiry & expands academic lexicon
        2. RetrievalAgent -> RAG search & ranking over provided paper corpus
        3. SummaryAgent -> thematic clustering & draft claims
        4. FactCheckAgent (Critic) -> audits claim entailment & flags unsupported claims
        5. ContradictionAgent -> scans cross-source academic divergence
        6. WriterAgent -> purges unsupported claims & compiles sourced literature review
        """
        pipeline_start = time.time()
        run_id = f"RUN-{int(time.time()*1000)}"
        trace: List[Dict[str, Any]] = []
        shared_state: Dict[str, Any] = {
            "run_id": run_id,
            "question": question,
            "architecture": "Pipeline with RAG and a Critic Architecture"
        }

        # -------------------------------------------------------------
        # STEP 1: Query Agent (Decomposition & Expansion)
        # -------------------------------------------------------------
        query_out = self.query_agent.execute(
            question=question,
            trace=trace,
            shared_state=shared_state
        )
        sub_queries = query_out.get("sub_queries", [question])
        expanded_queries = query_out.get("expanded_queries", sub_queries)

        # -------------------------------------------------------------
        # STEP 2: Retrieval Agent (Grounded Corpus RAG)
        # -------------------------------------------------------------
        passages_pool = get_paper_passages(custom_corpus) if custom_corpus else None
        retrieval_out = self.retrieval_agent.execute(
            sub_queries=expanded_queries,
            custom_passages=passages_pool,
            trace=trace,
            shared_state=shared_state
        )
        passages = retrieval_out.get("passages", [])

        # -------------------------------------------------------------
        # STEP 3: Summary Agent (Theme Clustering & Draft Synthesis)
        # -------------------------------------------------------------
        summary_out = self.summary_agent.execute(
            question=question,
            passages=passages,
            trace=trace,
            shared_state=shared_state
        )
        candidate_claims = list(summary_out.get("candidate_claims", []))

        # Optional Critic Test: Inject an intentional unsupported hallucination
        if inject_unsupported_claim:
            fake_claim = {
                "claim_id": f"Claim-{len(candidate_claims)+1}-INJECTED",
                "theme": "Empirical Performance & Complexity",
                "claim_text": "Quantum optical processors achieved 99.99% accuracy at zero electrical power consumption [P99].",
                "cited_tag": "[P99]",
                "source_paper": "Hallucinated Paper Not In Corpus",
                "source_authors": "Fake Author et al.",
                "source_year": 2026,
                "grounding_passage": "None"
            }
            candidate_claims.append(fake_claim)
            shared_state["candidate_claims"] = candidate_claims

        # -------------------------------------------------------------
        # STEP 4: Fact-Check Agent (The Critic - Entailment Audit Gate)
        # -------------------------------------------------------------
        fact_check_out = self.fact_check_agent.execute(
            candidate_claims=candidate_claims,
            passages=passages,
            trace=trace,
            shared_state=shared_state
        )
        audited_claims = fact_check_out.get("audited_claims", [])

        # -------------------------------------------------------------
        # STEP 5: Contradiction Agent (Cross-Source Divergence)
        # -------------------------------------------------------------
        contradiction_out = self.contradiction_agent.execute(
            passages=passages,
            claims=audited_claims,
            trace=trace,
            shared_state=shared_state
        )
        contradiction_dossier = contradiction_out.get("contradiction_dossier", {})

        # -------------------------------------------------------------
        # STEP 6: Writer Agent (Purging Unsupported Claims & Report Assembly)
        # -------------------------------------------------------------
        writer_out = self.writer_agent.execute(
            audited_claims=audited_claims,
            passages=passages,
            contradiction_dossier=contradiction_dossier,
            question=question,
            trace=trace,
            shared_state=shared_state
        )
        report = writer_out.get("report", {})
        retained_claims = writer_out.get("retained_claims", [])
        dropped_claims = writer_out.get("dropped_claims", [])
        verified_themes = report.get("verified_themes", summary_out.get("themes", []))

        total_pipeline_ms = round((time.time() - pipeline_start) * 1000, 2)

        result = {
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "architecture": "Pipeline with RAG and a Critic Architecture",
            "agents_executed": [
                self.query_agent.agent_name,
                self.retrieval_agent.agent_name,
                self.summary_agent.agent_name,
                self.fact_check_agent.agent_name,
                self.contradiction_agent.agent_name,
                self.writer_agent.agent_name
            ],
            "metrics": {
                "total_duration_ms": total_pipeline_ms,
                "sub_queries_count": len(sub_queries),
                "passages_retrieved": len(passages),
                "candidate_claims": len(candidate_claims),
                "retained_claims": len(retained_claims),
                "dropped_claims": len(dropped_claims),
                "contradictions_identified": len(contradiction_dossier.get("dossiers", []))
            },
            "sub_queries": sub_queries,
            "expanded_queries": expanded_queries,
            "passages": passages,
            "themes": verified_themes,
            "audited_claims": audited_claims,
            "retained_claims": retained_claims,
            "dropped_claims": dropped_claims,
            "contradictions": contradiction_dossier,
            "final_report": report,
            "shared_state_keys": list(shared_state.keys()),
            "agent_trace": trace
        }

        self._append_to_run_log(result)
        return result

    def _append_to_run_log(self, run_record: Dict[str, Any]):
        """Appends run record to append-only run log."""
        try:
            log_entry = {
                "run_id": run_record["run_id"],
                "timestamp": run_record["timestamp"],
                "question": run_record["question"],
                "architecture": run_record["architecture"],
                "agents_executed": run_record["agents_executed"],
                "duration_ms": run_record["metrics"]["total_duration_ms"],
                "retained_claims_count": run_record["metrics"]["retained_claims"],
                "dropped_claims_count": run_record["metrics"]["dropped_claims"],
                "contradictions_count": run_record["metrics"]["contradictions_identified"],
                "trace_steps": len(run_record["agent_trace"])
            }
            with open(RUN_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to append to run log: {e}")
