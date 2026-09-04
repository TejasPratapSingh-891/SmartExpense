from datetime import date
from sqlalchemy import func
from app import db
from app.models import Transaction, Budget, User
from app.utils import get_month_date_range, get_previous_month_year

def calculate_financial_health_score(user_id, year=None, month=None):
    today = date.today()
    year = year or today.year
    month = month or today.month

    start_date, end_date = get_month_date_range(year, month)
    prev_month, prev_year = get_previous_month_year(year, month)
    prev_start_date, prev_end_date = get_month_date_range(prev_year, prev_month)

    user = db.session.get(User, user_id)
    monthly_target = user.monthly_income_target if user else 50000.0

    # 1. Savings Rate Component (Max 40 points)
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

    savings = income - expense
    savings_rate = (savings / income * 100) if income > 0 else 0.0

    if income <= 0:
        savings_pts = 10.0
    elif savings_rate >= 50:
        savings_pts = 40.0
    elif savings_rate >= 35:
        savings_pts = 35.0
    elif savings_rate >= 20:
        savings_pts = 28.0
    elif savings_rate >= 10:
        savings_pts = 18.0
    elif savings_rate >= 0:
        savings_pts = 10.0
    else:
        savings_pts = 0.0

    # 2. Budget Discipline Component (Max 30 points)
    budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).all()
    if not budgets:
        # If no budget defined, assign reasonable neutral score
        budget_pts = 22.0
        budget_compliance_pct = 75.0
        budget_status = 'No active category budgets defined.'
    else:
        passed = 0
        for b in budgets:
            b_spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
                Transaction.user_id == user_id,
                Transaction.category_id == b.category_id,
                Transaction.type == 'expense',
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).scalar() or 0.0
            if b_spent <= b.monthly_limit:
                passed += 1
        compliance_ratio = passed / len(budgets)
        budget_compliance_pct = round(compliance_ratio * 100, 1)
        budget_pts = round(compliance_ratio * 30.0, 1)
        budget_status = f'{passed}/{len(budgets)} budgets within limit'

    # 3. Expense Control / Growth Component (Max 20 points)
    prev_expense = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= prev_start_date,
        Transaction.date <= prev_end_date
    ).scalar() or 0.0

    if prev_expense > 0:
        exp_growth = ((expense - prev_expense) / prev_expense) * 100
    else:
        exp_growth = 0.0

    if exp_growth <= 0:
        growth_pts = 20.0
    elif exp_growth <= 5:
        growth_pts = 17.0
    elif exp_growth <= 15:
        growth_pts = 13.0
    elif exp_growth <= 30:
        growth_pts = 8.0
    else:
        growth_pts = 4.0

    # 4. Income Stability & Cash Buffer (Max 10 points)
    if income >= monthly_target and savings > 0:
        stability_pts = 10.0
    elif savings > 0:
        stability_pts = 8.0
    elif income > 0:
        stability_pts = 5.0
    else:
        stability_pts = 2.0

    # Total Score
    total_score = round(savings_pts + budget_pts + growth_pts + stability_pts)
    total_score = max(0, min(100, total_score))

    # Grade determination
    if total_score >= 80:
        grade = 'Excellent'
        grade_color = '#10B981' # Emerald
        badge_class = 'badge-success'
    elif total_score >= 65:
        grade = 'Good'
        grade_color = '#3B82F6' # Blue
        badge_class = 'badge-primary'
    elif total_score >= 50:
        grade = 'Fair'
        grade_color = '#F59E0B' # Amber
        badge_class = 'badge-warning'
    else:
        grade = 'Needs Attention'
        grade_color = '#EF4444' # Rose
        badge_class = 'badge-danger'

    # Generate tailored improvement tips
    tips = []
    if savings_pts < 30:
        tips.append('Boost your savings rate above 30% to gain +10 health points.')
    if budget_pts < 25:
        tips.append('Keep all category expenditures within limits to boost budget discipline score.')
    if growth_pts < 15:
        tips.append(f'Recent monthly expenses grew {exp_growth:.1f}%. Trimming discretionary expenses will recover +7 points.')
    if not tips:
        tips.append('You are maintaining world-class financial discipline! Keep your savings pacing strong.')

    return {
        'score': total_score,
        'grade': grade,
        'grade_color': grade_color,
        'badge_class': badge_class,
        'savings_rate': round(savings_rate, 1),
        'breakdown': {
            'savings_rate': {
                'score': round(savings_pts, 1),
                'max': 40,
                'label': f'{savings_rate:.1f}% Savings Rate'
            },
            'budget_discipline': {
                'score': round(budget_pts, 1),
                'max': 30,
                'label': budget_status
            },
            'spending_growth': {
                'score': round(growth_pts, 1),
                'max': 20,
                'label': f'{exp_growth:+.1f}% MoM Spending'
            },
            'income_stability': {
                'score': round(stability_pts, 1),
                'max': 10,
                'label': 'Positive Cash Surplus' if savings > 0 else 'Deficit'
            }
        },
        'tips': tips
    }
