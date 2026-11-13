"""
Academic Research Assistant Team (CSE476 - Group 16)
Architecture: Pipeline with RAG and a Critic Architecture
Framework: Microsoft Semantic Kernel
"""

from app.agents.query_agent import QueryAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.summary_agent import SummaryAgent
from app.agents.fact_check_agent import FactCheckAgent
from app.agents.contradiction_agent import ContradictionAgent
from app.agents.writer_agent import WriterAgent
from app.agents.orchestrator import AcademicPipelineOrchestrator
from app.agents.corpus import DEFAULT_PAPER_CORPUS, get_paper_passages

__all__ = [
    "QueryAgent",
    "RetrievalAgent",
    "SummaryAgent",
    "FactCheckAgent",
    "ContradictionAgent",
    "WriterAgent",
    "AcademicPipelineOrchestrator",
    "DEFAULT_PAPER_CORPUS",
    "get_paper_passages"
]
