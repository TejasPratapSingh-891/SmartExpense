from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not identifier or not password:
            flash('Please provide both username/email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter(
            (User.username.ilike(identifier)) | (User.email.ilike(identifier))
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.dashboard'))
        else:
            flash('Invalid credentials. Please verify username/password.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not full_name or not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please pick another.', 'warning')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please login.', 'warning')
            return render_template('auth/register.html')

        new_user = User(
            full_name=full_name,
            username=username,
            email=email,
            currency_symbol='₹',
            monthly_income_target=50000.0
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Registration successful! Welcome to SmartExpense.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            full_name = request.form.get('full_name', '').strip()
            currency = request.form.get('currency_symbol', '₹').strip()
            try:
                monthly_target = float(request.form.get('monthly_income_target', 50000.0))
            except ValueError:
                monthly_target = 50000.0

            if full_name:
                current_user.full_name = full_name
            current_user.currency_symbol = currency
            current_user.monthly_income_target = monthly_target
            db.session.commit()
            flash('Profile preferences updated successfully!', 'success')

        elif action == 'change_password':
            old_pass = request.form.get('old_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_pass = request.form.get('confirm_password', '')

            if not current_user.check_password(old_pass):
                flash('Current password is incorrect.', 'danger')
            elif len(new_pass) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
            elif new_pass != confirm_pass:
                flash('New passwords do not match.', 'danger')
            else:
                current_user.set_password(new_pass)
                db.session.commit()
                flash('Password changed successfully!', 'success')

        return redirect(url_for('auth.settings'))

    return render_template('settings.html', user=current_user)

@auth_bp.route('/seed-demo', methods=['POST'])
@login_required
def seed_demo():
    from seed import seed_demo_data_for_user
    seed_demo_data_for_user(current_user.id)
    flash('Sample financial data (income, expenses, budgets) loaded successfully!', 'success')
    return redirect(url_for('main.dashboard'))
