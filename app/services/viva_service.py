import logging
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.paper import ResearchPaper
from app.models.paper_chunk import PaperChunk
from app.services.groq_service import get_groq_client, call_groq_completion

logger = logging.getLogger(__name__)

def query_paper_rag(paper_id: int, user_id: int, question: str, top_k: int = 4) -> Dict[str, Any]:
    """
    Executes deep TF-IDF RAG over the stored database chunks of a specific research paper.
    """
    paper = ResearchPaper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return {"answer": "Paper not found or unauthorized.", "sources": []}
        
    chunks = PaperChunk.query.filter_by(paper_id=paper_id, user_id=user_id).order_by(PaperChunk.chunk_index).all()
    if not chunks:
        # Fallback to abstract/metadata if no full-text chunks exist
        meta_context = f"Title: {paper.title}\nAuthors: {paper.authors}\nAbstract: {paper.abstract}\nKeywords: {paper.keywords}"
        return {
            "answer": (
                "⚠️ **Full paper has not been chunked into the database yet.**\n\n"
                "To enable deep paragraph-by-paragraph questioning, please upload the paper's PDF "
                "or paste its full text in the 'Upload & Index Full Paper' tab above.\n\n"
                f"**Based on saved paper metadata:**\n{meta_context[:500]}..."
            ),
            "sources": [],
            "needs_chunking": True
        }
        
    chunk_docs = [c.content for c in chunks]
    
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(chunk_docs)
        query_vec = vectorizer.transform([question])
        
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
        ranked_indices = similarities.argsort()[::-1]
        
        top_chunks: List[Tuple[PaperChunk, float]] = []
        for idx in ranked_indices[:top_k]:
            score = float(similarities[idx])
            top_chunks.append((chunks[idx], score))
            
        context_blocks = []
        source_details = []
        for chunk, score in top_chunks:
            source_details.append({
                "chunk_index": chunk.chunk_index,
                "section_title": chunk.section_title or f"Chunk #{chunk.chunk_index}",
                "score": round(score, 4),
                "word_count": chunk.word_count,
                "snippet": chunk.content[:160] + "..." if len(chunk.content) > 160 else chunk.content
            })
            context_blocks.append(
                f"[Source Chunk #{chunk.chunk_index} | Section: {chunk.section_title or 'General'}]\n{chunk.content}"
            )
            
        context_str = "\n\n".join(context_blocks)
        
        client = get_groq_client()
        if not client:
            return {
                "answer": (
                    f"**Relevant Chunks Found ({len(top_chunks)} chunks indexed):**\n\n"
                    + "\n\n".join([f"**Chunk #{c['chunk_index']} ({c['section_title']}):**\n{c['snippet']}" for c in source_details])
                    + "\n\n*(Note: Configure GROQ_API_KEY in .env for comprehensive LLM reasoning)*"
                ),
                "sources": source_details
            }
            
        prompt = f"""You are an elite academic research advisor and Viva Voce (Oral Defense) examiner.
You are assisting a researcher who is studying the paper: "{paper.title}".

Context Extracted from Stored Paper Chunks (Database):
{context_str}

Researcher's Question:
{question}

Instructions:
1. Provide a rigorous, detailed, and technically precise answer based on the provided paper chunks.
2. Cite the specific chunk numbers and sections where relevant (e.g., "[Chunk #2, Methodology]").
3. Explain technical methodologies, equations, benchmarks, or arguments clearly.
4. If the retrieved chunks do not contain enough details to fully answer, state what is covered and what requires reviewing other sections of the paper.
5. Format your output with clear Markdown headings and bullet points.
"""

        messages = [
            {"role": "system", "content": "You are an expert scientific examiner and academic defense mentor."},
            {"role": "user", "content": prompt}
        ]
        
        answer_text = call_groq_completion(client, messages, temperature=0.2, max_tokens=1500)
        return {
            "answer": answer_text,
            "sources": source_details,
            "total_indexed_chunks": len(chunks)
        }
    except Exception as e:
        logger.error(f"Error in deep paper RAG: {e}")
        return {
            "answer": f"Error performing RAG on paper chunks: {str(e)}",
            "sources": []
        }

def generate_viva_defense_pack(paper_id: int, user_id: int) -> Dict[str, Any]:
    """
    Generates a structured Viva Voce preparation package with examiner questions and model defenses.
    """
    paper = ResearchPaper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return {"error": "Paper not found."}
        
    chunks = PaperChunk.query.filter_by(paper_id=paper_id, user_id=user_id).order_by(PaperChunk.chunk_index).all()
    
    # Construct representative document context from key chunks
    if chunks:
        # Sample chunks across the paper: beginning, middle, and end
        num_chunks = len(chunks)
        selected_chunks = []
        if num_chunks <= 6:
            selected_chunks = chunks
        else:
            selected_chunks.extend(chunks[:2]) # Intro/abstract
            mid = num_chunks // 2
            selected_chunks.extend(chunks[mid-1:mid+2]) # Methodology/experiments
            selected_chunks.extend(chunks[-2:]) # Conclusion
            
        paper_context = "\n\n".join([
            f"[Chunk #{c.chunk_index} - {c.section_title}]: {c.content[:700]}"
            for c in selected_chunks
        ])
    else:
        paper_context = (
            f"Title: {paper.title}\n"
            f"Authors: {paper.authors}\n"
            f"Journal: {paper.journal} ({paper.publication_year})\n"
            f"Keywords: {paper.keywords}\n"
            f"Abstract: {paper.abstract}\n"
        )
        
    client = get_groq_client()
    if not client:
        return {
            "success": True,
            "markdown": (
                f"# Viva Voce Defense Prep: {paper.title}\n\n"
                "### 🎓 Standard Examiner Defense Rounds (Fallback Mode)\n\n"
                "**Round 1: Research Motivation & Problem Definition**\n"
                "- *Examiner:* What is the primary research gap that this work addresses, and why were existing methods insufficient?\n"
                f"- *Context:* Based on publication in {paper.journal or 'literature'}, focusing on {paper.keywords or paper.title}.\n\n"
                "**Round 2: Methodological Choices & Technical Depth**\n"
                "- *Examiner:* Why was this specific experimental or computational approach selected over baseline alternatives?\n\n"
                "**Round 3: Cross-Examination & Critical Limitations**\n"
                "- *Examiner:* Under what conditions does your approach fail, and what are the main threats to validity?\n\n"
                "*(Configure GROQ_API_KEY for dynamic Llama-3.3 full-text defense generation)*"
            ),
            "chunks_used": len(chunks)
        }
        
    prompt = f"""You are a distinguished Senior Academic Examiner presiding over a PhD/Master's thesis Viva Voce examination.
The candidate will defend the following research paper:

Paper Title: {paper.title}
Authors: {paper.authors or 'N/A'}
Publication: {paper.journal or 'N/A'} ({paper.publication_year or 'N/A'})

Paper Content / Stored Chunks:
{paper_context[:4500]}

Generate a comprehensive, rigorous, and highly realistic **Viva Voce Defense Package** for this paper.
Structure your response in Markdown with the following exact sections:

# 🎓 Viva Voce Oral Defense Preparation Pack

## 1. Executive Defense Elevator Pitch (2 Minutes)
(A crisp 120-second spoken opening defense: Problem, Unique Value Proposition, Core Method, and Measured Impact)

## 2. Round 1: Motivation & Academic Contribution
- **Q1:** (Challenging question on problem definition and why prior baselines fail)
  - **Examiner's Intent:** (What the committee is secretly testing)
  - **Recommended Defense Answer:** (Evidence-based response citing specific methods/results)
- **Q2:** (Question on scope and novelty)
  - **Examiner's Intent:**
  - **Recommended Defense Answer:**

## 3. Round 2: Technical Methodology & Architectural Justification
- **Q3:** (Granular question dissecting algorithmic choices, hyper-parameters, assumptions, or dataset curation)
  - **Examiner's Intent:**
  - **Recommended Defense Answer:**
- **Q4:** (Question on ablation studies, baseline comparisons, and statistical significance)
  - **Examiner's Intent:**
  - **Recommended Defense Answer:**

## 4. Round 3: Tough Cross-Examination & Adversarial Grilling
- **Q5 (Examiner Trap Question):** (A skeptical, adversarial question highlighting potential weaknesses, edge cases, or computational complexity)
  - **Examiner's Trap:** (Why this is dangerous if unprepared)
  - **Diplomatic & Strong Defense:** (How to counter-defend without being defensive)
- **Q6:** (Question regarding scalability, generalization, and practical deployment constraints)
  - **Recommended Defense:**

## 5. Defense Cheat Sheet & Key Formulas/Insights to Memorize
(Bullet points of vital numbers, key theoretical guarantees, and punchy summary takeaways for the candidate to remember)
"""

    try:
        messages = [
            {"role": "system", "content": "You are a world-class academic examiner crafting challenging viva defense curricula."},
            {"role": "user", "content": prompt}
        ]
        pack_text = call_groq_completion(client, messages, temperature=0.3, max_tokens=2500)
        return {
            "success": True,
            "markdown": pack_text,
            "chunks_used": len(chunks)
        }
    except Exception as e:
        logger.error(f"Error generating viva defense pack: {e}")
        return {"error": f"Failed to generate Viva prep package: {str(e)}"}

def evaluate_viva_defense_response(paper_id: int, user_id: int, examiner_question: str, candidate_answer: str) -> Dict[str, Any]:
    """
    Evaluates a candidate's defense response against the paper chunks and provides examiner grading.
    """
    paper = ResearchPaper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return {"error": "Paper not found."}
        
    rag_data = query_paper_rag(paper_id, user_id, examiner_question, top_k=3)
    context_sources = "\n\n".join([f"[{s['section_title']}]: {s['snippet']}" for s in rag_data.get("sources", [])])
    
    client = get_groq_client()
    if not client:
        return {
            "success": True,
            "score": 8,
            "feedback": "Answer submitted. (Configure GROQ_API_KEY for real-time examiner score & critiques.)"
        }
        
    prompt = f"""You are a strict, constructive academic Viva Voce committee examiner.
Paper Title: {paper.title}

Context from Paper:
{context_sources}

Examiner Question:
{examiner_question}

Candidate's Defense Answer:
{candidate_answer}

Evaluate the candidate's response in markdown:
### 🎯 Examiner Score: [X/10]
### ✅ Strengths in Defense:
- (What points were well argued)
### ⚠️ Vulnerabilities / Gaps:
- (What was omitted, vague, or scientifically hand-waving)
### 💎 Model Academic Defense Response:
(How a PhD candidate should ideally answer this question with poise and scientific rigor)
"""

    try:
        messages = [
            {"role": "system", "content": "You are a tough but fair academic viva examiner grading student oral defense answers."},
            {"role": "user", "content": prompt}
        ]
        critique = call_groq_completion(client, messages, temperature=0.2, max_tokens=1000)
        return {
            "success": True,
            "evaluation": critique
        }
    except Exception as e:
        logger.error(f"Error evaluating viva answer: {e}")
        return {"error": f"Failed to evaluate answer: {str(e)}"}
