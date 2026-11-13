import logging
import requests
from app.services.doi_service import normalize_doi

logger = logging.getLogger(__name__)

STYLE_MAP = {
    'apa': 'text/x-bibliography; style=apa',
    'mla': 'text/x-bibliography; style=mla',
    'ieee': 'text/x-bibliography; style=ieee',
    'bibtex': 'application/x-bibtex'
}

def format_citation(paper, style: str = 'APA') -> str:
    style_lower = style.lower()
    doi = normalize_doi(paper.doi) if paper.doi else ""
    
    if doi:
        headers = {'Accept': STYLE_MAP.get(style_lower, 'text/x-bibliography; style=apa')}
        try:
            url = f"https://doi.org/{doi}"
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200 and resp.text.strip():
                return resp.text.strip()
        except Exception as e:
            logger.debug(f"DOI content negotiation failed for {doi}: {e}")

    authors = paper.authors or "Unknown Author"
    title = paper.title or "Untitled"
    journal = paper.journal or "Journal"
    year = paper.publication_year or "n.d."
    doi_str = f"https://doi.org/{doi}" if doi else (paper.url or "")
    
    if style_lower == 'apa':
        return f"{authors} ({year}). {title}. {journal}. {doi_str}".strip()
    elif style_lower == 'mla':
        return f'{authors}. "{title}." {journal}, {year}. {doi_str}'.strip()
    elif style_lower == 'ieee':
        return f'{authors}, "{title}," {journal}, {year}. {doi_str}'.strip()
    elif style_lower == 'bibtex':
        first_author = authors.split(',')[0].split()[0] if authors else "article"
        cite_key = "".join(c for c in f"{first_author}{year}" if c.isalnum())
        return (
            f"@article{{{cite_key},\n"
            f"  author = {{{authors}}},\n"
            f"  title = {{{title}}},\n"
            f"  journal = {{{journal}}},\n"
            f"  year = {{{year}}},\n"
            f"  doi = {{{doi}}},\n"
            f"  url = {{{doi_str}}}\n"
            f"}}"
        )
    else:
        return f"{authors} ({year}). {title}. {journal}."

