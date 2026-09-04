from datetime import date
import calendar
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Transaction, Budget
from app.services.analytics_service import get_monthly_kpis, get_spending_by_category, get_burn_rate_metrics
from app.services.health_score import calculate_financial_health_score
from app.utils import get_month_date_range

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods=['GET'])
@login_required
def index():
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    start_date, end_date = get_month_date_range(year, month)

    kpis = get_monthly_kpis(current_user.id, year, month)
    category_spending = get_spending_by_category(current_user.id, year, month)
    burn_rate = get_burn_rate_metrics(current_user.id, year, month)
    health_score = calculate_financial_health_score(current_user.id, year, month)

    # All transactions for selected month
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).order_by(Transaction.date.asc()).all()

    # Budget compliance in report
    budgets = Budget.query.filter_by(user_id=current_user.id, month=month, year=year).all()
    budget_audit = []
    for b in budgets:
        b_spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == b.category_id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0.0

        budget_audit.append({
            'category': b.category.name if b.category else 'Unknown',
            'limit': b.monthly_limit,
            'spent': b_spent,
            'variance': b.monthly_limit - b_spent,
            'status': 'Over Budget' if b_spent > b.monthly_limit else 'Within Budget'
        })

    # Available months for report switcher
    months_list = [(m, calendar.month_name[m]) for m in range(1, 13)]
    years_list = [today.year - 1, today.year, today.year + 1]

    return render_template(
        'reports.html',
        kpis=kpis,
        category_spending=category_spending,
        burn_rate=burn_rate,
        health_score=health_score,
        transactions=transactions,
        budget_audit=budget_audit,
        selected_month=month,
        selected_year=year,
        month_name=calendar.month_name[month],
        months_list=months_list,
        years_list=years_list,
        generated_date=date.today().strftime('%B %d, %Y')
    )
