import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("SESSION_SECRET") or secrets.token_hex(16)
    
    # Database config (SQLite local dev by default)
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'agentic_research.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    DEFAULT_DB_URI = f"sqlite:///{db_path}"
    
    db_url = os.environ.get("DATABASE_URL", DEFAULT_DB_URI)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI & Multi-Agent Model Configuration
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
    CROSSREF_EMAIL = os.environ.get("CROSSREF_EMAIL", "researcher@example.com")
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}
