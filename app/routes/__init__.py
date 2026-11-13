from app.routes.auth import auth_bp
from app.routes.academic_team import academic_team_bp
from app.routes.papers import papers_bp
from app.routes.search import search_bp
from app.routes.viva import viva_bp

__all__ = [
    'auth_bp',
    'academic_team_bp',
    'papers_bp',
    'search_bp',
    'viva_bp'
]

