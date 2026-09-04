import calendar
from datetime import date, datetime, timedelta
from sqlalchemy import func, extract
from app import db
from app.models import Transaction, Category, Budget
from app.utils import get_month_date_range, get_previous_month_year

def get_monthly_kpis(user_id, year=None, month=None):
    today = date.today()
    year = year or today.year
    month = month or today.month

    start_date, end_date = get_month_date_range(year, month)
    prev_month, prev_year = get_previous_month_year(year, month)
    prev_start_date, prev_end_date = get_month_date_range(prev_year, prev_month)

    # Current month aggregates
    income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or 0.0

    expense = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or 0.0

    net_savings = income - expense
    savings_rate = (net_savings / income * 100) if income > 0 else 0.0

    # Previous month aggregates
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

    prev_net_savings = prev_income - prev_expense
    prev_savings_rate = (prev_net_savings / prev_income * 100) if prev_income > 0 else 0.0

    # Calculate MoM percentage changes
    def calc_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    income_change = calc_change(income, prev_income)
    expense_change = calc_change(expense, prev_expense)
    savings_change = calc_change(net_savings, prev_net_savings)
    savings_rate_change = savings_rate - prev_savings_rate

    # Savings rate status label
    if savings_rate >= 40:
        rate_status = 'Excellent'
        rate_color = 'success'
    elif savings_rate >= 20:
        rate_status = 'Good'
        rate_color = 'primary'
    elif savings_rate >= 10:
        rate_status = 'Moderate'
        rate_color = 'warning'
    else:
        rate_status = 'Low'
        rate_color = 'danger'

    return {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'income': income,
        'expense': expense,
        'net_savings': net_savings,
        'savings_rate': round(savings_rate, 1),
        'rate_status': rate_status,
        'rate_color': rate_color,
        'income_change': round(income_change, 1),
        'expense_change': round(expense_change, 1),
        'savings_change': round(savings_change, 1),
        'savings_rate_change': round(savings_rate_change, 1),
        'prev_income': prev_income,
        'prev_expense': prev_expense,
        'prev_net_savings': prev_net_savings,
        'prev_savings_rate': round(prev_savings_rate, 1)
    }

def get_spending_by_category(user_id, year=None, month=None):
    today = date.today()
    year = year or today.year
    month = month or today.month

    start_date, end_date = get_month_date_range(year, month)

    results = db.session.query(
        Category.id,
        Category.name,
        Category.color,
        Category.icon,
        func.coalesce(func.sum(Transaction.amount), 0.0).label('total_amount'),
        func.count(Transaction.id).label('tx_count')
    ).join(Transaction, Transaction.category_id == Category.id).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(Category.id, Category.name, Category.color, Category.icon).order_by(
        func.sum(Transaction.amount).desc()
    ).all()

    total_expense = sum(r.total_amount for r in results) or 1.0 # prevent div by zero

    categories_data = []
    for r in results:
        percentage = round((r.total_amount / total_expense) * 100, 1)
        categories_data.append({
            'category_id': r.id,
            'name': r.name,
            'color': r.color,
            'icon': r.icon,
            'amount': r.total_amount,
            'count': r.tx_count,
            'percentage': percentage
        })

    return {
        'total_expense': total_expense if results else 0.0,
        'categories': categories_data
    }

def get_daily_spending_trend(user_id, year=None, month=None):
    today = date.today()
    year = year or today.year
    month = month or today.month

    _, num_days = calendar.monthrange(year, month)
    start_date, end_date = get_month_date_range(year, month)

    txs = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()

    # Map daily totals
    daily_map = {day: 0.0 for day in range(1, num_days + 1)}
    cumulative_map = {}
    running_total = 0.0

    for tx in txs:
        day = tx.date.day
        daily_map[day] = daily_map.get(day, 0.0) + tx.amount

    labels = [f"{calendar.month_abbr[month]} {d}" for d in range(1, num_days + 1)]
    daily_amounts = [round(daily_map[d], 2) for d in range(1, num_days + 1)]

    cumulative_amounts = []
    for d in range(1, num_days + 1):
        # only accumulate up to current day if looking at current month
        if year == today.year and month == today.month and d > today.day:
            break
        running_total += daily_map[d]
        cumulative_amounts.append(round(running_total, 2))

    return {
        'labels': labels,
        'daily_amounts': daily_amounts,
        'cumulative_amounts': cumulative_amounts,
        'days_in_month': num_days
    }

def get_monthly_history(user_id, months_count=6):
    today = date.today()
    history = []

    for i in range(months_count - 1, -1, -1):
        # Calculate target year and month
        target_month = today.month - i
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1

        start_date, end_date = get_month_date_range(target_year, target_month)

        inc = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0.0

        exp = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0.0

        history.append({
            'year': target_year,
            'month': target_month,
            'label': f"{calendar.month_abbr[target_month]} '{str(target_year)[2:]}",
            'income': round(inc, 2),
            'expense': round(exp, 2),
            'savings': round(inc - exp, 2)
        })

    return history

def get_burn_rate_metrics(user_id, year=None, month=None):
    today = date.today()
    year = year or today.year
    month = month or today.month

    _, total_days = calendar.monthrange(year, month)
    start_date, end_date = get_month_date_range(year, month)

    elapsed_days = today.day if (year == today.year and month == today.month) else total_days
    elapsed_days = max(1, elapsed_days)

    total_expense = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or 0.0

    avg_daily = total_expense / elapsed_days
    projected = avg_daily * total_days
    remaining_days = total_days - elapsed_days

    highest_expense_tx = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).order_by(Transaction.amount.desc()).first()

    return {
        'elapsed_days': elapsed_days,
        'remaining_days': remaining_days,
        'total_days': total_days,
        'total_expense': total_expense,
        'avg_daily_spend': round(avg_daily, 2),
        'projected_month_end': round(projected, 2),
        'highest_expense': highest_expense_tx.to_dict() if highest_expense_tx else None
    }
