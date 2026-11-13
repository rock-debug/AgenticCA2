import re
from app.services.crossref_service import get_crossref_metadata_by_doi

DOI_REGEX = re.compile(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+')

def normalize_doi(doi: str) -> str:
    if not doi:
        return ""
    cleaned = doi.strip()
    cleaned = re.sub(r'^https?://(dx\.)?doi\.org/', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned

def validate_doi(doi: str) -> bool:
    norm = normalize_doi(doi)
    return bool(DOI_REGEX.match(norm))

def fetch_doi_metadata(doi: str):
    norm = normalize_doi(doi)
    if not norm:
        return None
    return get_crossref_metadata_by_doi(norm)
