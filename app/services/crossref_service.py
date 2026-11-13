import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

def search_crossref(query: str, limit: int = 10):
    if not query or not query.strip():
        return []
        
    email = current_app.config.get("CROSSREF_EMAIL", "researcher@example.com")
    url = "https://api.crossref.org/works"
    params = {
        'query': query,
        'rows': min(limit, 50),
        'sort': 'relevance',
        'order': 'desc',
        'mailto': email
    }
    
    headers = {
        'User-Agent': f'JournalPatentTracker/1.0 (mailto:{email})'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Crossref API returned status code {response.status_code}")
            return []
            
        data = response.json()
        items = data.get('message', {}).get('items', [])
        
        results = []
        for item in items:
            title_list = item.get('title', [])
            title = title_list[0] if title_list else 'Untitled'
            
            authors = _format_authors(item.get('author', []))
            
            container = item.get('container-title', [])
            journal = container[0] if container else ''
            
            published = item.get('published', {}) or item.get('issued', {})
            date_parts = published.get('date-parts', [[]])
            year = date_parts[0][0] if date_parts and date_parts[0] else None
            
            doi = item.get('DOI', '')
            url_link = item.get('URL', f"https://doi.org/{doi}" if doi else '')
            abstract = item.get('abstract', '')
            
            if abstract and isinstance(abstract, str):
                import re
                abstract = re.sub(r'<[^>]+>', '', abstract).strip()
                
            results.append({
                'title': title,
                'authors': authors,
                'journal': journal,
                'publication_year': year,
                'doi': doi,
                'url': url_link,
                'abstract': abstract,
                'keywords': ', '.join(item.get('subject', [])) if item.get('subject') else ''
            })
            
        return results
        
    except requests.exceptions.Timeout:
        logger.error("Crossref API request timed out")
        return []
    except Exception as e:
        logger.error(f"Error calling Crossref API: {e}")
        return []

def get_crossref_metadata_by_doi(doi: str):
    if not doi:
        return None
        
    clean_doi = doi.replace('https://doi.org/', '').replace('http://doi.org/', '').strip()
    email = current_app.config.get("CROSSREF_EMAIL", "researcher@example.com")
    url = f"https://api.crossref.org/works/{clean_doi}"
    headers = {'User-Agent': f'JournalPatentTracker/1.0 (mailto:{email})'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        data = response.json()
        item = data.get('message', {})
        
        title_list = item.get('title', [])
        title = title_list[0] if title_list else 'Untitled'
        
        authors = _format_authors(item.get('author', []))
        container = item.get('container-title', [])
        journal = container[0] if container else ''
        
        published = item.get('published', {}) or item.get('issued', {})
        date_parts = published.get('date-parts', [[]])
        year = date_parts[0][0] if date_parts and date_parts[0] else None
        
        abstract = item.get('abstract', '')
        if abstract and isinstance(abstract, str):
            import re
            abstract = re.sub(r'<[^>]+>', '', abstract).strip()
            
        return {
            'title': title,
            'authors': authors,
            'journal': journal,
            'publication_year': year,
            'doi': item.get('DOI', clean_doi),
            'url': item.get('URL', f"https://doi.org/{clean_doi}"),
            'abstract': abstract,
            'keywords': ', '.join(item.get('subject', [])) if item.get('subject') else ''
        }
    except Exception as e:
        logger.error(f"Error fetching DOI metadata: {e}")
        return None

def _format_authors(author_list):
    if not author_list or not isinstance(author_list, list):
        return ""
    authors = []
    for author in author_list:
        family = author.get('family', '')
        given = author.get('given', '')
        if family and given:
            authors.append(f"{family}, {given}")
        elif family:
            authors.append(family)
        elif author.get('name'):
            authors.append(author.get('name'))
    return '; '.join(authors)
