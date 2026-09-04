from datetime import date
import calendar
from sqlalchemy import func
from app import db
from app.models import Transaction, Category, Budget
from app.utils import get_month_date_range, get_previous_month_year

def generate_smart_insights(user_id, year=None, month=None):
    today = date.today()
    year = year or today.year
    month = month or today.month

    start_date, end_date = get_month_date_range(year, month)
    prev_month, prev_year = get_previous_month_year(year, month)
    prev_start_date, prev_end_date = get_month_date_range(prev_year, prev_month)
    _, total_days = calendar.monthrange(year, month)
    elapsed_days = today.day if (year == today.year and month == today.month) else total_days
    remaining_days = max(0, total_days - elapsed_days)

    insights = []

    # 1. Check Category MoM Spikes
    current_cat_spends = dict(db.session.query(
        Category.name,
        func.coalesce(func.sum(Transaction.amount), 0.0)
    ).join(Transaction, Transaction.category_id == Category.id).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(Category.name).all())

    prev_cat_spends = dict(db.session.query(
        Category.name,
        func.coalesce(func.sum(Transaction.amount), 0.0)
    ).join(Transaction, Transaction.category_id == Category.id).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= prev_start_date,
        Transaction.date <= prev_end_date
    ).group_by(Category.name).all())

    for cat_name, cur_amount in current_cat_spends.items():
        prev_amount = prev_cat_spends.get(cat_name, 0.0)
        if prev_amount > 500:
            diff = cur_amount - prev_amount
            pct = (diff / prev_amount) * 100
            if pct >= 20 and diff >= 800:
                insights.append({
                    'id': f'spike-{cat_name.lower().replace(" ", "-")}',
                    'type': 'warning',
                    'badge': 'Spending Alert',
                    'icon': 'trending-up',
                    'title': f'{cat_name} expenses surged {pct:.0f}%',
                    'message': f'Your {cat_name} spend reached ₹{cur_amount:,.0f} compared to ₹{prev_amount:,.0f} last month (+₹{diff:,.0f}). Consider auditing recent transactions in this category.',
                    'action_label': 'View Transactions',
                    'action_url': f'/transactions?category={cat_name}'
                })
                break # Only show highest spike to avoid flooding

    # 2. Check Budget Thresholds (80% and Overrun)
    budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).all()
    for b in budgets:
        spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.user_id == user_id,
            Transaction.category_id == b.category_id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0.0

        utilization = (spent / b.monthly_limit * 100) if b.monthly_limit > 0 else 0
        cat_name = b.category.name if b.category else 'Category'

        if spent > b.monthly_limit:
            over = spent - b.monthly_limit
            insights.append({
                'id': f'budget-over-{b.id}',
                'type': 'danger',
                'badge': 'Budget Exceeded',
                'icon': 'alert-triangle',
                'title': f'{cat_name} exceeded by ₹{over:,.0f}',
                'message': f'You have consumed {utilization:.0f}% of your ₹{b.monthly_limit:,.0f} allocation. Total spend is ₹{spent:,.0f}.',
                'action_label': 'Adjust Budget',
                'action_url': '/budgets'
            })
        elif utilization >= 80:
            remaining = b.monthly_limit - spent
            insights.append({
                'id': f'budget-warning-{b.id}',
                'type': 'warning',
                'badge': 'Budget Alert',
                'icon': 'alert-circle',
                'title': f'{cat_name} budget is {utilization:.0f}% used',
                'message': f'₹{remaining:,.0f} remaining with {remaining_days} days left in the billing period. Moderate daily pace to avoid an overrun.',
                'action_label': 'Manage Budgets',
                'action_url': '/budgets'
            })

    # 3. Discretionary Savings Opportunity
    discretionary_names = ['Shopping & Lifestyle', 'Entertainment', 'Food & Dining']
    discretionary_spend = sum(current_cat_spends.get(name, 0.0) for name in discretionary_names)
    if discretionary_spend >= 2500:
        potential_save = discretionary_spend * 0.20
        insights.append({
            'id': 'opportunity-discretionary',
            'type': 'opportunity',
            'badge': 'Savings Opportunity',
            'icon': 'sparkles',
            'title': f'Save ~₹{potential_save:,.0f} by trimming 20% on lifestyle',
            'message': f'You have spent ₹{discretionary_spend:,.0f} across dining, entertainment, and shopping this month. A 20% haircut could boost your net savings by ₹{potential_save:,.0f}.',
            'action_label': 'Review Spending',
            'action_url': '/analytics'
        })

    # 4. Savings Rate Momentum
    cur_income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or 0.0

    cur_expense = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or 0.0

    prev_income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income',
        Transaction.date >= prev_start_date,
        Transaction.date <= prev_end_date
    ).scalar() or 0.0

    prev_expense = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= prev_start_date,
        Transaction.date <= prev_end_date
    ).scalar() or 0.0

    cur_rate = ((cur_income - cur_expense) / cur_income * 100) if cur_income > 0 else 0
    prev_rate = ((prev_income - prev_expense) / prev_income * 100) if prev_income > 0 else 0

    if cur_rate > prev_rate and cur_income > 0:
        rate_diff = cur_rate - prev_rate
        insights.append({
            'id': 'trend-savings-positive',
            'type': 'positive',
            'badge': 'Positive Trend',
            'icon': 'award',
            'title': f'Savings rate improved from {prev_rate:.1f}% to {cur_rate:.1f}%',
            'message': f'Outstanding discipline! You are retaining {rate_diff:.1f}% more of your monthly income than last month.',
            'action_label': 'View Analytics',
            'action_url': '/analytics'
        })
    elif cur_rate >= 50 and cur_income > 0:
        insights.append({
            'id': 'trend-savings-high',
            'type': 'positive',
            'badge': 'Elite Saver',
            'icon': 'shield-check',
            'title': f'Maintaining a {cur_rate:.1f}% Savings Rate',
            'message': 'You are operating well above the standard 20% savings benchmark. Excellent capital retention this cycle.',
            'action_label': 'View Financial Health',
            'action_url': '/analytics'
        })

    # 5. Default encouraging insight if list is still small
    if len(insights) < 2:
        insights.append({
            'id': 'general-liquidity-check',
            'type': 'info',
            'badge': 'Smart Tip',
            'icon': 'lightbulb',
            'title': 'Track Every Expense for Highest Accuracy',
            'message': 'Log your daily UPI and card expenditures promptly to keep the financial health algorithm and pacing models up to date.',
            'action_label': '+ Add Transaction',
            'action_url': '/transactions?action=new'
        })

    return insights
