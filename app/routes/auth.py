from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('academic_team.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'researcher').strip()
        
        if not username or not email or not password:
            flash('All fields are required.', 'warning')
            return render_template('auth/register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please login.', 'danger')
            return render_template('auth/register.html')
            
        if role not in ['researcher', 'admin']:
            role = 'researcher'
            
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('academic_team.index'))
        
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = bool(request.form.get('remember'))
        
        if not username_or_email or not password:
            flash('Please enter both username/email and password.', 'warning')
            return render_template('auth/login.html')
            
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email.lower())).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('academic_team.index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
