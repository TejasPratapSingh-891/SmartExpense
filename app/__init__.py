import os
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Ensure instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to access your financial dashboard.'
    login_manager.login_message_category = 'warning'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Template context processors for global variables
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        currency = '₹'
        if current_user.is_authenticated and hasattr(current_user, 'currency_symbol'):
            currency = current_user.currency_symbol or '₹'
        return {
            'CURRENCY': currency,
            'APP_NAME': 'SmartExpense',
            'APP_TAGLINE': 'Personal Financial Analytics Platform'
        }

    # Template filters
    @app.template_filter('currency')
    def format_currency(value, symbol=None):
        if value is None:
            value = 0.0
        if symbol is None:
            from flask_login import current_user
            symbol = current_user.currency_symbol if current_user.is_authenticated else '₹'
        try:
            val_float = float(value)
            # Indian numbering format or standard with commas
            return f"{symbol}{val_float:,.2f}"
        except (ValueError, TypeError):
            return f"{symbol}{value}"

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.transactions import transactions_bp
    from app.routes.budgets import budgets_bp
    from app.routes.analytics import analytics_bp
    from app.routes.reports import reports_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(budgets_bp, url_prefix='/budgets')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()
        _init_default_categories()

    return app

def _init_default_categories():
    from app.models import Category
    defaults = [
        # Expenses
        ('Food & Dining', 'expense', 'utensils', '#F59E0B'),
        ('Transportation & Travel', 'expense', 'car', '#3B82F6'),
        ('Shopping & Lifestyle', 'expense', 'shopping-bag', '#EC4899'),
        ('Bills & Utilities', 'expense', 'zap', '#8B5CF6'),
        ('Entertainment', 'expense', 'film', '#06B6D4'),
        ('Healthcare & Wellness', 'expense', 'heart-pulse', '#10B981'),
        ('Education & Books', 'expense', 'book-open', '#6366F1'),
        ('Housing & Rent', 'expense', 'home', '#EF4444'),
        ('Miscellaneous', 'expense', 'tag', '#64748B'),
        # Incomes
        ('Salary', 'income', 'briefcase', '#10B981'),
        ('Freelance & Consulting', 'income', 'laptop', '#3B82F6'),
        ('Investments & Dividends', 'income', 'trending-up', '#8B5CF6'),
        ('Bonus & Awards', 'income', 'award', '#F59E0B'),
        ('Other Income', 'income', 'dollar-sign', '#14B8A6'),
    ]
    for name, cat_type, icon, color in defaults:
        existing = Category.query.filter_by(name=name, type=cat_type, user_id=None).first()
        if not existing:
            cat = Category(name=name, type=cat_type, icon=icon, color=color, user_id=None)
            db.session.add(cat)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
