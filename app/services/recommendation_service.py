import logging
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from app.models.paper import ResearchPaper
from app.services.crossref_service import search_crossref

logger = logging.getLogger(__name__)

def generate_user_recommendations(user_id: int) -> Dict[str, Any]:
    papers = ResearchPaper.query.filter_by(user_id=user_id).all()
    if not papers or len(papers) == 0:
        return {
            "personalized": False,
            "message": "Insufficient saved research data. Add a few research papers to your library to get personalized AI recommendations.",
            "top_keywords": [],
            "recommendations": []
        }
        
    corpus = []
    for p in papers:
        text = f"{p.title} {p.keywords or ''} {p.abstract or ''}".strip()
        if text:
            corpus.append(text)
            
    if not corpus:
        return {
            "personalized": False,
            "message": "Saved papers do not contain enough title/abstract text for personalization.",
            "top_keywords": [],
            "recommendations": []
        }
        
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=20)
        vectorizer.fit(corpus)
        feature_names = vectorizer.get_feature_names_out()
        
        top_keywords = list(feature_names[:5])
        search_query = " ".join(top_keywords[:3])
        
        external_results = search_crossref(search_query, limit=6)
        
        user_dois = {p.doi.lower() for p in papers if p.doi}
        recommendations = []
        
        for item in external_results:
            doi = (item.get('doi') or '').lower()
            if doi and doi in user_dois:
                continue
            recommendations.append(item)
            if len(recommendations) >= 5:
                break
                
        return {
            "personalized": True,
            "message": f"Recommendations based on your interest in: {', '.join(top_keywords)}",
            "top_keywords": top_keywords,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return {
            "personalized": False,
            "message": f"Unable to generate recommendations: {str(e)}",
            "top_keywords": [],
            "recommendations": []
        }
