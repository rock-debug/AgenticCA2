import pytest
from app import create_app
from app.extensions import db
from app.models import User, ResearchPaper

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def researcher_user(app):
    user = User(username='test_researcher', email='researcher@test.com', role='researcher')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def second_user(app):
    user = User(username='other_researcher', email='other@test.com', role='researcher')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def admin_user(app):
    user = User(username='test_admin', email='admin@test.com', role='admin')
    user.set_password('adminpassword')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def auth_client(client, researcher_user):
    client.post('/login', data={
        'username': 'test_researcher',
        'password': 'password123'
    }, follow_redirects=True)
    return client

@pytest.fixture
def admin_client(client, admin_user):
    client.post('/login', data={
        'username': 'test_admin',
        'password': 'adminpassword'
    }, follow_redirects=True)
    return client

