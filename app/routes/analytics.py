from datetime import date
import calendar
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.services.analytics_service import (
    get_monthly_kpis, 
    get_spending_by_category, 
    get_burn_rate_metrics, 
    get_monthly_history
)
from app.services.health_score import calculate_financial_health_score

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('', methods=['GET'])
@login_required
def index():
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    kpis = get_monthly_kpis(current_user.id, year, month)
    category_spending = get_spending_by_category(current_user.id, year, month)
    burn_rate = get_burn_rate_metrics(current_user.id, year, month)
    health_score = calculate_financial_health_score(current_user.id, year, month)
    history = get_monthly_history(current_user.id, months_count=6)

    return render_template(
        'analytics.html',
        kpis=kpis,
        category_spending=category_spending,
        burn_rate=burn_rate,
        health_score=health_score,
        history=history,
        selected_month=month,
        selected_year=year,
        month_name=calendar.month_name[month]
    )
