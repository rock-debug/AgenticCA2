from datetime import datetime, timezone
from app.extensions import db

class PaperChunk(db.Model):
    __tablename__ = 'paper_chunks'
    
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('research_papers.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    section_title = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    char_count = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<PaperChunk paper={self.paper_id} index={self.chunk_index} section={self.section_title}>'

