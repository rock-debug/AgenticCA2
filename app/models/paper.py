from datetime import datetime, timezone
from app.extensions import db

class ResearchPaper(db.Model):
    __tablename__ = 'research_papers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.Text, nullable=True)
    abstract = db.Column(db.Text, nullable=True)
    journal = db.Column(db.String(255), nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    doi = db.Column(db.String(100), nullable=True, index=True)
    url = db.Column(db.String(500), nullable=True)
    keywords = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Unread')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    chunks = db.relationship('PaperChunk', backref='paper', lazy=True, cascade="all, delete-orphan", order_by="PaperChunk.chunk_index")
    
    @property
    def chunk_count(self):
        return len(self.chunks) if self.chunks else 0

    def __repr__(self):
        return f'<ResearchPaper {self.title}>'

