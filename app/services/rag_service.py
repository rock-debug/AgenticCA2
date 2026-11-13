import logging
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.paper import ResearchPaper
from app.services.groq_service import answer_rag_question

logger = logging.getLogger(__name__)

def query_rag_system(user_id: int, question: str, top_k: int = 3) -> Dict[str, Any]:
    papers = ResearchPaper.query.filter_by(user_id=user_id).all()
    if not papers:
        return {
            "answer": "You currently have no saved research papers in your library. Please add papers first.",
            "sources": []
        }
        
    documents = []
    paper_map = []
    
    for paper in papers:
        doc_text = f"Title: {paper.title}. "
        if paper.authors:
            doc_text += f"Authors: {paper.authors}. "
        if paper.journal:
            doc_text += f"Journal: {paper.journal}. "
        if paper.keywords:
            doc_text += f"Keywords: {paper.keywords}. "
        if paper.abstract:
            doc_text += f"Abstract: {paper.abstract}. "
            
        documents.append(doc_text)
        paper_map.append(paper)
        
    if not documents:
        return {
            "answer": "No readable content found in your saved research papers.",
            "sources": []
        }
        
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)
        question_vec = vectorizer.transform([question])
        
        similarities = cosine_similarity(question_vec, tfidf_matrix).flatten()
        ranked_indices = similarities.argsort()[::-1]
        
        relevant_items: List[Tuple[ResearchPaper, float, str]] = []
        for idx in ranked_indices[:top_k]:
            score = similarities[idx]
            if score > 0.02:
                relevant_items.append((paper_map[idx], score, documents[idx]))
                
        if not relevant_items:
            return {
                "answer": "No relevant saved research papers were found in your library matching your question.",
                "sources": []
            }
            
        context_blocks = []
        sources = []
        for paper, score, doc_text in relevant_items:
            sources.append({
                "id": paper.id,
                "title": paper.title,
                "journal": paper.journal,
                "year": paper.publication_year,
                "doi": paper.doi,
                "score": float(score)
            })
            context_blocks.append(f"--- Paper: {paper.title} ({paper.publication_year or 'N/A'}) ---\n{doc_text}")
            
        context_str = "\n\n".join(context_blocks)
        return answer_rag_question(question, context_str, sources)
        
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}")
        return {
            "answer": f"Error executing RAG search over research papers: {str(e)}",
            "sources": []
        }
