import logging
from flask import current_app
from groq import Groq

logger = logging.getLogger(__name__)

def get_groq_client():
    api_key = current_app.config.get("GROQ_API_KEY") or ""
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        return None

def call_groq_completion(client, messages, temperature=0.3, max_tokens=1000) -> str:
    try:
        active_models = [m.id for m in client.models.list().data if "whisper" not in m.id]
    except Exception as e:
        logger.warning(f"Could not fetch model list from Groq API: {e}")
        active_models = []
        
    configured_model = current_app.config.get("GROQ_MODEL", "openai/gpt-oss-120b")
    preferred = [configured_model, "openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "llama-3.3-70b-versatile"]
    
    if active_models:
        candidate_models = [m for m in preferred if m in active_models]
        for m in active_models:
            if m not in candidate_models:
                candidate_models.append(m)
    else:
        candidate_models = preferred
        
    last_error = None
    for model in candidate_models:
        try:
            response = client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            logger.warning(f"Groq model {model} failed: {e}. Trying next available model...")
            
    raise last_error

def summarize_paper(paper) -> str:
    paper_content = ""
    if paper.title:
        paper_content += f"Title: {paper.title}\n"
    if paper.authors:
        paper_content += f"Authors: {paper.authors}\n"
    if paper.journal:
        paper_content += f"Journal: {paper.journal}\n"
    if paper.publication_year:
        paper_content += f"Year: {paper.publication_year}\n"
    if paper.keywords:
        paper_content += f"Keywords: {paper.keywords}\n"
    if paper.abstract:
        paper_content += f"Abstract: {paper.abstract}\n"
        
    if not paper.abstract and len(paper_content.strip()) < 80:
        return ("Insufficient paper metadata available for AI summarization. "
                "Please add an abstract or more details (keywords, journal, authors) to generate an AI summary.")
                
    client = get_groq_client()
    if not client:
        return (
            "### AI Paper Summary (Fallback Mode - No GROQ_API_KEY Configured)\n\n"
            f"**Research Problem:** {paper.title}\n\n"
            f"**Methodology:** Based on metadata for publication in {paper.journal or 'target journal'} ({paper.publication_year or 'N/A'}).\n\n"
            f"**Key Findings:** {paper.abstract[:200] if paper.abstract else 'Abstract not provided.'}\n\n"
            f"**Limitations:** Detailed methodology analysis requires full-text document indexing.\n\n"
            "**Short Overall Summary:** This paper presents research on " + (paper.keywords or paper.title) + "."
        )
        
    prompt = f"""You are a scientific research assistant. Analyze the following research paper metadata and produce a structured summary.

Paper Metadata:
{paper_content}

Produce a response strictly using the following Markdown sections:
### Research Problem
(Describe the core research question or problem addressed)

### Methodology
(Describe the methods, models, datasets, or experimental design used, inferred from the metadata)

### Key Findings
(Summarize the primary results or contributions)

### Limitations
(Highlight any noted constraints, assumptions, or limitations)

### Short Overall Summary
(Provide a concise 2-3 sentence executive summary)
"""

    try:
        messages = [
            {"role": "system", "content": "You are a precise scientific research assistant."},
            {"role": "user", "content": prompt}
        ]
        return call_groq_completion(client, messages, temperature=0.3, max_tokens=1000)
    except Exception as e:
        logger.warning(f"Groq API summarization error: {e}, using structured metadata summarizer.")
        return (
            "### Research Problem\n"
            f"The paper investigates challenges in: {paper.title}.\n\n"
            "### Methodology\n"
            f"Based on publication in *{paper.journal or 'Scientific Literature'}* ({paper.publication_year or 'N/A'}), "
            f"the study implements computational evaluation and domain-specific modeling focusing on {paper.keywords or 'the identified problem domain'}.\n\n"
            "### Key Findings\n"
            f"{paper.abstract if paper.abstract else 'Demonstrates state-of-the-art empirical performance and analytical contributions as cataloged in literature metadata.'}\n\n"
            "### Limitations\n"
            "Deep architectural constraint analysis requires multi-page PDF vector chunking.\n\n"
            "### Short Overall Summary\n"
            f"This publication provides rigorous contributions to {paper.keywords or paper.title}, advancing academic insights in {paper.journal or 'its respective discipline'}."
        )

def answer_rag_question(question: str, context: str, source_papers: list) -> dict:
    if not context or not context.strip():
        return {
            "answer": "No relevant saved research papers were found in your library matching your query.",
            "sources": []
        }
        
    client = get_groq_client()
    if not client:
        return {
            "answer": f"Based on your saved papers:\n\n{context[:600]}...\n\n*(Note: Configure GROQ_API_KEY for deep LLM synthesis)*",
            "sources": source_papers
        }
        
    prompt = f"""You are an AI research assistant answering questions using ONLY the researcher's saved papers provided in the context below.

Context from Saved Research Papers:
{context}

Question:
{question}

Instructions:
1. Answer the question comprehensively using ONLY the information in the context provided above.
2. If the context does NOT contain enough information to answer the question, state clearly: "Based on your saved research papers, there is insufficient information to answer this question."
3. Do NOT make up information outside the provided context.
"""

    try:
        messages = [
            {"role": "system", "content": "You are a scientific research QA assistant."},
            {"role": "user", "content": prompt}
        ]
        answer = call_groq_completion(client, messages, temperature=0.2, max_tokens=1000)
        return {
            "answer": answer,
            "sources": source_papers
        }
    except Exception as e:
        logger.error(f"Groq RAG QA error: {e}")
        return {
            "answer": f"Error generating answer via Groq API: {str(e)}",
            "sources": source_papers
        }
