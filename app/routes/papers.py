from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ResearchPaper
from app.services.doi_service import normalize_doi, fetch_doi_metadata

papers_bp = Blueprint('papers', __name__)

@papers_bp.route('/papers')
@login_required
def index():
    query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    papers_query = ResearchPaper.query.filter_by(user_id=current_user.id)
    
    if query:
        search_pattern = f"%{query}%"
        papers_query = papers_query.filter(
            (ResearchPaper.title.ilike(search_pattern)) |
            (ResearchPaper.authors.ilike(search_pattern)) |
            (ResearchPaper.journal.ilike(search_pattern)) |
            (ResearchPaper.keywords.ilike(search_pattern))
        )
        
    if status_filter:
        papers_query = papers_query.filter_by(status=status_filter)
        
    papers = papers_query.order_by(ResearchPaper.created_at.desc()).all()
    return render_template('papers/index.html', papers=papers, query=query, status_filter=status_filter)

@papers_bp.route('/papers/fetch_doi', methods=['POST'])
@login_required
def fetch_doi():
    doi = request.form.get('doi', '').strip()
    if request.is_json:
        data = request.get_json() or {}
        doi = data.get('doi', doi).strip()
        
    if not doi:
        return jsonify({"success": False, "error": "DOI is required."}), 400
        
    metadata = fetch_doi_metadata(doi)
    if not metadata or 'error' in metadata:
        return jsonify({"success": False, "error": "Could not fetch metadata for the specified DOI."}), 404
        
    return jsonify({"success": True, "metadata": metadata})

@papers_bp.route('/papers/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        authors = request.form.get('authors', '').strip()
        journal = request.form.get('journal', '').strip()
        publication_year = request.form.get('publication_year', '').strip()
        doi = request.form.get('doi', '').strip()
        url = request.form.get('url', '').strip()
        abstract = request.form.get('abstract', '').strip()
        keywords = request.form.get('keywords', '').strip()
        status = request.form.get('status', 'Unread').strip()
        
        if not title:
            flash('Paper title is required.', 'danger')
            return render_template('papers/create.html')
            
        norm_doi = normalize_doi(doi) if doi else None
        
        if norm_doi:
            existing = ResearchPaper.query.filter_by(user_id=current_user.id, doi=norm_doi).first()
            if existing:
                flash(f'A research paper with DOI {norm_doi} already exists in your library.', 'warning')
                return redirect(url_for('papers.detail', paper_id=existing.id))
                
        year_val = int(publication_year) if publication_year and publication_year.isdigit() else None
        
        paper = ResearchPaper(
            user_id=current_user.id,
            title=title,
            authors=authors,
            journal=journal,
            publication_year=year_val,
            doi=norm_doi or doi,
            url=url,
            abstract=abstract,
            keywords=keywords,
            status=status
        )
        
        db.session.add(paper)
        db.session.commit()
        
        flash('Research paper added successfully to agent corpus!', 'success')
        return redirect(url_for('papers.detail', paper_id=paper.id))
        
    return render_template('papers/create.html')

@papers_bp.route('/papers/<int:paper_id>')
@login_required
def detail(paper_id):
    paper = db.session.get(ResearchPaper, paper_id)
    if not paper:
        abort(404)
    if paper.user_id != current_user.id:
        abort(403)
        
    return render_template('papers/detail.html', paper=paper)

@papers_bp.route('/papers/<int:paper_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(paper_id):
    paper = db.session.get(ResearchPaper, paper_id)
    if not paper:
        abort(404)
    if paper.user_id != current_user.id:
        abort(403)
        
    if request.method == 'POST':
        paper.title = request.form.get('title', '').strip()
        paper.authors = request.form.get('authors', '').strip()
        paper.journal = request.form.get('journal', '').strip()
        
        pub_year = request.form.get('publication_year', '').strip()
        paper.publication_year = int(pub_year) if pub_year and pub_year.isdigit() else None
        
        doi_input = request.form.get('doi', '').strip()
        paper.doi = normalize_doi(doi_input) if doi_input else ""
        paper.url = request.form.get('url', '').strip()
        paper.abstract = request.form.get('abstract', '').strip()
        paper.keywords = request.form.get('keywords', '').strip()
        paper.status = request.form.get('status', paper.status).strip()
        
        if not paper.title:
            flash('Title cannot be empty.', 'danger')
            return render_template('papers/edit.html', paper=paper)
            
        db.session.commit()
        flash('Research paper updated successfully.', 'success')
        return redirect(url_for('papers.detail', paper_id=paper.id))
        
    return render_template('papers/edit.html', paper=paper)

@papers_bp.route('/papers/<int:paper_id>/delete', methods=['POST'])
@login_required
def delete(paper_id):
    paper = db.session.get(ResearchPaper, paper_id)
    if not paper:
        abort(404)
    if paper.user_id != current_user.id:
        abort(403)
        
    db.session.delete(paper)
    db.session.commit()
    
    flash('Research paper deleted from corpus.', 'info')
    return redirect(url_for('papers.index'))

