from datetime import date
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Transaction
from app.services.analytics_service import (
    get_daily_spending_trend,
    get_spending_by_category,
    get_monthly_history,
    get_monthly_kpis
)

api_bp = Blueprint('api', __name__)

@api_bp.route('/dashboard/chart-data')
@login_required
def dashboard_chart_data():
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    trend = get_daily_spending_trend(current_user.id, year, month)
    cat_data = get_spending_by_category(current_user.id, year, month)

    category_labels = [c['name'] for c in cat_data['categories']]
    category_amounts = [c['amount'] for c in cat_data['categories']]
    category_colors = [c['color'] for c in cat_data['categories']]

    return jsonify({
        'trend': trend,
        'categories': {
            'labels': category_labels,
            'amounts': category_amounts,
            'colors': category_colors
        }
    })

@api_bp.route('/analytics/monthly-trend')
@login_required
def monthly_trend():
    history = get_monthly_history(current_user.id, months_count=6)
    labels = [h['label'] for h in history]
    income_series = [h['income'] for h in history]
    expense_series = [h['expense'] for h in history]
    savings_series = [h['savings'] for h in history]

    return jsonify({
        'labels': labels,
        'income': income_series,
        'expense': expense_series,
        'savings': savings_series
    })

@api_bp.route('/transactions/<int:tx_id>')
@login_required
def get_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    return jsonify(tx.to_dict())
