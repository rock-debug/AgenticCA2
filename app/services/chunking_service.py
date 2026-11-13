import re
import logging
import io
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
from app.extensions import db
from app.models.paper_chunk import PaperChunk
from app.models.paper import ResearchPaper

logger = logging.getLogger(__name__)

# Common academic section markers
SECTION_PATTERNS = [
    r'^(?:[0-9IVX]+\.?\s*)?(abstract)\b',
    r'^(?:[0-9IVX]+\.?\s*)?(introduction)\b',
    r'^(?:[0-9IVX]+\.?\s*)?(background|related\s+work)\b',
    r'^(?:[0-9IVX]+\.?\s*)?(methodology|methods|proposed\s+approach|model\s+architecture|architecture|system\s+design)\b',
    r'^(?:[0-9IVX]+\.?\s*)?(experimental\s+setup|experiments|implementation\s+details|evaluation)\b',
    r'^(?:[0-9IVX]+\.?\s*)?(results|findings|empirical\s+analysis)\b',
    r'^(?:[0-9IVX]+\.?\s*)?(discussion|ablation\s+study|comparative\s+analysis)\b',
    r'^(?:[0-9IVX]+\.?\s*)?(limitations|threats\s+to\s+validity)\b',
    r'^(?:[0-9IVX]+\.?\s*)?(conclusion|concluding\s+remarks|future\s+work)\b',
    r'^(?:[0-9IVX]+\.?\s*)?(references|bibliography)\b'
]

def extract_text_from_pdf(file_stream) -> Tuple[str, int]:
    """
    Extracts plain text from an uploaded PDF stream or bytes buffer.
    Returns (extracted_text, page_count).
    """
    try:
        reader = PdfReader(file_stream)
        page_count = len(reader.pages)
        pages_text = []
        
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(f"[Page {idx + 1}]\n{text.strip()}")
                
        full_text = "\n\n".join(pages_text)
        # Normalize whitespace while preserving paragraphs
        full_text = re.sub(r'\r\n', '\n', full_text)
        full_text = re.sub(r'[ \t]+', ' ', full_text)
        return full_text, page_count
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise ValueError(f"Could not parse PDF file: {str(e)}")

def detect_section_header(line: str) -> str:
    """Attempts to identify academic paper section headers from a line of text."""
    clean_line = line.strip().lower()
    if len(clean_line) > 80:
        return ""
    for pat in SECTION_PATTERNS:
        match = re.search(pat, clean_line, re.IGNORECASE)
        if match:
            # Capitalize matched header
            header = match.group(1).title()
            return header
    return ""

def chunk_text(text: str, target_words: int = 500, overlap_words: int = 80) -> List[Dict[str, Any]]:
    """
    Semantically chunks paper text into overlapping windows, tracking section context.
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]
        
    chunks = []
    current_words = []
    current_section = "Introduction / Overview"
    chunk_index = 1
    
    for para in paragraphs:
        # Check if first line of paragraph is a section header
        first_line = para.split('\n')[0].strip()
        detected_sec = detect_section_header(first_line)
        if detected_sec:
            current_section = detected_sec
            
        words = para.split()
        current_words.extend(words)
        
        # When accumulator reaches target size, create a chunk
        if len(current_words) >= target_words:
            chunk_content = " ".join(current_words)
            chunks.append({
                "chunk_index": chunk_index,
                "section_title": current_section,
                "content": chunk_content,
                "word_count": len(current_words),
                "char_count": len(chunk_content)
            })
            chunk_index += 1
            # Maintain overlap for semantic continuity
            current_words = current_words[-overlap_words:]
            
    # Trailing words
    if current_words and len(current_words) > 30:
        chunk_content = " ".join(current_words)
        chunks.append({
            "chunk_index": chunk_index,
            "section_title": current_section,
            "content": chunk_content,
            "word_count": len(current_words),
            "char_count": len(chunk_content)
        })
        
    return chunks

def ingest_paper_full_text(paper_id: int, user_id: int, full_text: str, source_label: str = "Full Document") -> Dict[str, Any]:
    """
    Chunks and stores the full text of a paper in the PaperChunk database table.
    Overwrites previous chunks for the paper to ensure a clean index.
    """
    paper = ResearchPaper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        raise ValueError("Paper not found or unauthorized.")
        
    if not full_text or len(full_text.strip()) < 100:
        raise ValueError("Provided document text is too short to chunk and index.")
        
    # Remove existing chunks for this paper
    PaperChunk.query.filter_by(paper_id=paper_id).delete()
    db.session.commit()
    
    raw_chunks = chunk_text(full_text)
    if not raw_chunks:
        raise ValueError("Unable to generate text chunks from the provided content.")
        
    db_chunks = []
    sections_found = set()
    total_words = 0
    
    for c in raw_chunks:
        sections_found.add(c["section_title"])
        total_words += c["word_count"]
        chunk_obj = PaperChunk(
            paper_id=paper_id,
            user_id=user_id,
            chunk_index=c["chunk_index"],
            section_title=c["section_title"],
            content=c["content"],
            char_count=c["char_count"],
            word_count=c["word_count"]
        )
        db_chunks.append(chunk_obj)
        
    db.session.add_all(db_chunks)
    db.session.commit()
    
    logger.info(f"Ingested {len(db_chunks)} chunks ({total_words} words) for paper {paper_id}")
    return {
        "success": True,
        "paper_id": paper_id,
        "total_chunks": len(db_chunks),
        "total_words": total_words,
        "sections": sorted(list(sections_found)),
        "source": source_label
    }
