"""
Database Seeder for Agentic AI (CSE476 - Group 16)
Creates default researcher and admin accounts and populates the research corpus.
"""

from app import create_app
from app.extensions import db
from app.models import User, ResearchPaper, PaperChunk
from app.agents.corpus import DEFAULT_PAPER_CORPUS

def seed():
    app = create_app()
    with app.app_context():
        # Check if users already exist
        if User.query.filter_by(username='researcher').first():
            print("[INFO] Default users already exist in the database.")
            return

        print("[*] Creating default user accounts...")
        researcher = User(
            username='researcher',
            email='researcher@example.com',
            role='researcher'
        )
        researcher.set_password('password123')
        db.session.add(researcher)

        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        print("[*] Seeding research paper corpus from benchmark papers...")
        for p in DEFAULT_PAPER_CORPUS:
            paper = ResearchPaper(
                user_id=researcher.id,
                title=p['title'],
                authors=p['authors'],
                journal=p['journal'],
                publication_year=p['publication_year'],
                doi=p['doi'],
                abstract=p['abstract'],
                keywords='AI, Multi-Agent, RAG, Transformers, Deep Learning',
                status='Completed'
            )
            db.session.add(paper)
            db.session.flush()

            for idx, sec in enumerate(p.get('sections', []), 1):
                chunk = PaperChunk(
                    paper_id=paper.id,
                    user_id=researcher.id,
                    chunk_index=idx,
                    section_title=sec['section'],
                    content=sec['text'],
                    char_count=len(sec['text']),
                    word_count=len(sec['text'].split())
                )
                db.session.add(chunk)

        db.session.commit()
        print(f"[SUCCESS] Successfully seeded 2 default users and {len(DEFAULT_PAPER_CORPUS)} corpus papers!")
        print("  - Researcher: username='researcher', password='password123'")
        print("  - Admin:      username='admin', password='admin123'\n")

if __name__ == '__main__':
    seed()
