from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ResearchPaper
from app.services.crossref_service import search_crossref
from app.services.doi_service import normalize_doi

search_bp = Blueprint('search', __name__)

@search_bp.route('/search/crossref')
@login_required
def crossref():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        results = search_crossref(query, limit=12)
        
    return render_template('search/index.html', query=query, results=results)

@search_bp.route('/search/save_paper', methods=['POST'])
@login_required
def save_paper():
    title = request.form.get('title', '').strip()
    authors = request.form.get('authors', '').strip()
    journal = request.form.get('journal', '').strip()
    year_str = request.form.get('publication_year', '').strip()
    doi = request.form.get('doi', '').strip()
    url = request.form.get('url', '').strip()
    abstract = request.form.get('abstract', '').strip()
    keywords = request.form.get('keywords', '').strip()
    
    if not title:
        flash('Cannot save paper without a title.', 'danger')
        return redirect(url_for('search.crossref'))
        
    norm_doi = normalize_doi(doi) if doi else None
    
    if norm_doi:
        existing = ResearchPaper.query.filter_by(user_id=current_user.id, doi=norm_doi).first()
        if existing:
            flash(f'Paper "{title}" (DOI: {norm_doi}) is already in your library!', 'info')
            return redirect(url_for('papers.detail', paper_id=existing.id))
            
    pub_year = int(year_str) if year_str and year_str.isdigit() else None
    
    paper = ResearchPaper(
        user_id=current_user.id,
        title=title,
        authors=authors,
        journal=journal,
        publication_year=pub_year,
        doi=norm_doi or doi,
        url=url,
        abstract=abstract,
        keywords=keywords,
        status='Unread'
    )
    
    db.session.add(paper)
    db.session.commit()
    
    flash(f'Paper "{title}" saved to your personal library!', 'success')
    return redirect(url_for('papers.detail', paper_id=paper.id))
