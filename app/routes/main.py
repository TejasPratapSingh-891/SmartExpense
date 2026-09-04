from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import date
from app.models import Transaction, Category, Budget
from app.services.analytics_service import get_monthly_kpis, get_spending_by_category
from app.services.insights_engine import generate_smart_insights
from app.services.health_score import calculate_financial_health_score
from app.utils import get_user_categories

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    # Analytics & Services
    kpis = get_monthly_kpis(current_user.id, year, month)
    category_spending = get_spending_by_category(current_user.id, year, month)
    health_score = calculate_financial_health_score(current_user.id, year, month)
    insights = generate_smart_insights(current_user.id, year, month)

    # Recent Transactions (Limit 6)
    recent_transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(Transaction.date.desc(), Transaction.id.desc()).limit(6).all()

    # Categories for Quick Transaction Modal
    expense_categories = get_user_categories(current_user.id, 'expense')
    income_categories = get_user_categories(current_user.id, 'income')

    # Time of day greeting
    import datetime
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = 'Good morning'
    elif current_hour < 17:
        greeting = 'Good afternoon'
    else:
        greeting = 'Good evening'

    first_name = current_user.full_name.split()[0] if current_user.full_name else 'User'

    return render_template(
        'dashboard.html',
        kpis=kpis,
        category_spending=category_spending,
        health_score=health_score,
        insights=insights,
        recent_transactions=recent_transactions,
        expense_categories=expense_categories,
        income_categories=income_categories,
        greeting=greeting,
        first_name=first_name,
        today=today,
        selected_year=year,
        selected_month=month
    )
