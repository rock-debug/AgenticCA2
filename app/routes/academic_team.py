"""
Academic Research Assistant Team Route Blueprint
Interactive Web Interface & Execution API for Multi-Agent Pipeline.
"""

import os
import json
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, Response
from flask_login import login_required, current_user

from app.agents import AcademicPipelineOrchestrator, DEFAULT_PAPER_CORPUS
from app.models.paper import ResearchPaper

academic_team_bp = Blueprint('academic_team', __name__, url_prefix='/academic-team')

RUN_LOG_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "..", "..", "run_log.jsonl"
)


def load_recent_run_logs(limit: int = 10):
    """Reads recent entries from append-only run log."""
    logs = []
    if os.path.exists(RUN_LOG_PATH):
        try:
            with open(RUN_LOG_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in reversed(lines[-limit:]):
                    if line.strip():
                        logs.append(json.loads(line))
        except Exception:
            pass
    return logs


@academic_team_bp.route('/', methods=['GET'])
@login_required
def index():
    recent_logs = load_recent_run_logs(10)
    
    # Also fetch user's saved papers count
    user_papers_count = ResearchPaper.query.filter_by(user_id=current_user.id).count()

    preset_questions = [
        "What are the risks and coordination patterns in autonomous multi-agent workflows?",
        "Compare centralized orchestration vs decentralized blackboard architectures for autonomous agent systems.",
        "How does the Transformer self-attention mechanism overcome recurrence limitations in sequence transduction?",
        "What is the degradation problem in deep neural networks and how do residual identity shortcuts resolve it?"
    ]

    return render_template(
        'academic_team/index.html',
        recent_logs=recent_logs,
        user_papers_count=user_papers_count,
        preset_questions=preset_questions,
        default_corpus=DEFAULT_PAPER_CORPUS,
        result=None
    )


@academic_team_bp.route('/run', methods=['POST'])
@login_required
def run_pipeline():
    question = request.form.get('question', '').strip()
    inject_fake = request.form.get('inject_unsupported_claim') == 'on'
    use_user_papers = request.form.get('use_user_papers') == 'on'

    if not question:
        flash("Please enter a research question.", "warning")
        return redirect(url_for('academic_team.index'))

    # Build custom corpus if user requested their own saved papers
    custom_corpus = None
    if use_user_papers:
        user_papers = ResearchPaper.query.filter_by(user_id=current_user.id).all()
        if user_papers:
            custom_corpus = []
            for up in user_papers:
                custom_corpus.append({
                    "id": up.id,
                    "title": up.title,
                    "authors": up.authors or "Researcher Library",
                    "journal": up.journal or "Personal Library",
                    "publication_year": up.publication_year or 2024,
                    "doi": up.doi or "10.library/user",
                    "abstract": up.abstract or f"Paper title: {up.title}. Keywords: {up.keywords or ''}",
                    "sections": [
                        {"section": "Content", "text": c.content} for c in up.chunks
                    ] if up.chunks else []
                })

    orchestrator = AcademicPipelineOrchestrator()
    result = orchestrator.run_pipeline(
        question=question,
        custom_corpus=custom_corpus,
        inject_unsupported_claim=inject_fake
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify(result)

    recent_logs = load_recent_run_logs(10)
    user_papers_count = ResearchPaper.query.filter_by(user_id=current_user.id).count()

    preset_questions = [
        "What are the risks and coordination patterns in autonomous multi-agent workflows?",
        "Compare centralized orchestration vs decentralized blackboard architectures for autonomous agent systems.",
        "How does the Transformer self-attention mechanism overcome recurrence limitations in sequence transduction?",
        "What is the degradation problem in deep neural networks and how do residual identity shortcuts resolve it?"
    ]

    flash(f"Multi-Agent execution completed in {result['metrics']['total_duration_ms']}ms. Run ID: {result['run_id']}", "success")

    return render_template(
        'academic_team/index.html',
        recent_logs=recent_logs,
        user_papers_count=user_papers_count,
        preset_questions=preset_questions,
        default_corpus=DEFAULT_PAPER_CORPUS,
        result=result,
        submitted_question=question,
        inject_fake=inject_fake,
        use_user_papers=use_user_papers
    )


@academic_team_bp.route('/export-markdown', methods=['POST'])
@login_required
def export_markdown():
    content = request.form.get('markdown_content', '')
    title = request.form.get('report_title', 'literature_review')
    filename = f"{title.replace(' ', '_').lower()[:30]}.md"

    return Response(
        content,
        mimetype="text/markdown",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
