import io
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.paper import ResearchPaper
from app.models.paper_chunk import PaperChunk
from app.services.chunking_service import extract_text_from_pdf, ingest_paper_full_text
from app.services.viva_service import query_paper_rag, generate_viva_defense_pack, evaluate_viva_defense_response

viva_bp = Blueprint('viva', __name__, url_prefix='/viva')

@viva_bp.route('/')
@login_required
def index():
    papers = ResearchPaper.query.filter_by(user_id=current_user.id).order_by(ResearchPaper.updated_at.desc()).all()
    
    # Calculate stats
    total_papers = len(papers)
    indexed_papers = sum(1 for p in papers if p.chunk_count > 0)
    total_chunks = PaperChunk.query.filter_by(user_id=current_user.id).count()
    
    return render_template(
        'viva/index.html',
        papers=papers,
        total_papers=total_papers,
        indexed_papers=indexed_papers,
        total_chunks=total_chunks
    )

@viva_bp.route('/<int:paper_id>')
@login_required
def detail(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    if paper.user_id != current_user.id:
        abort(403)
        
    chunks = PaperChunk.query.filter_by(paper_id=paper_id, user_id=current_user.id).order_by(PaperChunk.chunk_index).all()
    total_words = sum(c.word_count for c in chunks)
    sections = sorted(list(set(c.section_title for c in chunks if c.section_title)))
    
    return render_template(
        'viva/detail.html',
        paper=paper,
        chunks=chunks,
        total_chunks=len(chunks),
        total_words=total_words,
        sections=sections
    )

@viva_bp.route('/<int:paper_id>/upload', methods=['POST'])
@login_required
def upload(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    if paper.user_id != current_user.id:
        abort(403)
        
    source_label = "Pasted Text"
    full_text = ""
    
    # Check if a PDF file was uploaded
    if 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        if pdf_file and pdf_file.filename.lower().endswith('.pdf'):
            try:
                extracted, page_count = extract_text_from_pdf(io.BytesIO(pdf_file.read()))
                full_text = extracted
                source_label = f"Uploaded PDF ({pdf_file.filename}, {page_count} pages)"
            except Exception as e:
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"error": f"Failed to parse PDF: {str(e)}"}), 400
                flash(f"PDF parsing error: {str(e)}", "danger")
                return redirect(url_for('viva.detail', paper_id=paper_id))
                
    # Fallback to pasted text
    if not full_text:
        full_text = request.form.get('paper_text', '').strip()
        if request.is_json:
            data = request.get_json() or {}
            full_text = data.get('paper_text', full_text).strip()
            
    if not full_text or len(full_text) < 100:
        msg = "Please provide a valid PDF file or at least 100 characters of paper text."
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": msg}), 400
        flash(msg, "warning")
        return redirect(url_for('viva.detail', paper_id=paper_id))
        
    try:
        result = ingest_paper_full_text(paper_id, current_user.id, full_text, source_label=source_label)
        msg = f"Successfully chunked and stored {result['total_chunks']} chunks ({result['total_words']} words) in the database."
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True,
                "message": msg,
                "total_chunks": result['total_chunks'],
                "total_words": result['total_words'],
                "sections": result['sections']
            })
        flash(msg, "success")
        return redirect(url_for('viva.detail', paper_id=paper_id))
    except Exception as e:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": str(e)}), 500
        flash(f"Chunking error: {str(e)}", "danger")
        return redirect(url_for('viva.detail', paper_id=paper_id))

@viva_bp.route('/<int:paper_id>/ask', methods=['POST'])
@login_required
def ask(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    if paper.user_id != current_user.id:
        abort(403)
        
    question = request.form.get('question', '').strip()
    if request.is_json:
        data = request.get_json() or {}
        question = data.get('question', question).strip()
        
    if not question:
        return jsonify({"error": "Question is required."}), 400
        
    rag_result = query_paper_rag(paper_id, current_user.id, question)
    return jsonify(rag_result)

@viva_bp.route('/<int:paper_id>/generate-pack', methods=['POST'])
@login_required
def generate_pack(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    if paper.user_id != current_user.id:
        abort(403)
        
    result = generate_viva_defense_pack(paper_id, current_user.id)
    return jsonify(result)

@viva_bp.route('/<int:paper_id>/evaluate', methods=['POST'])
@login_required
def evaluate(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    if paper.user_id != current_user.id:
        abort(403)
        
    data = request.get_json() if request.is_json else request.form
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    
    if not question or not answer:
        return jsonify({"error": "Both the examiner question and candidate answer are required."}), 400
        
    result = evaluate_viva_defense_response(paper_id, current_user.id, question, answer)
    return jsonify(result)

@viva_bp.route('/<int:paper_id>/clear-chunks', methods=['POST'])
@login_required
def clear_chunks(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    if paper.user_id != current_user.id:
        abort(403)
        
    PaperChunk.query.filter_by(paper_id=paper_id, user_id=current_user.id).delete()
    db.session.commit()
    flash("Paper chunks successfully removed from database.", "info")
    return redirect(url_for('viva.detail', paper_id=paper_id))
