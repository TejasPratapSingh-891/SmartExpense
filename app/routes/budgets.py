from datetime import date
import calendar
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Budget, Category, Transaction
from app.utils import get_user_categories, get_month_date_range

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('', methods=['GET'])
@login_required
def index():
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    start_date, end_date = get_month_date_range(year, month)
    _, total_days = calendar.monthrange(year, month)
    elapsed_days = today.day if (year == today.year and month == today.month) else total_days
    remaining_days = max(0, total_days - elapsed_days)

    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=month,
        year=year
    ).all()

    budget_items = []
    total_budgeted = 0.0
    total_spent_budgeted = 0.0

    for b in budgets:
        spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == b.category_id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0.0

        total_budgeted += b.monthly_limit
        total_spent_budgeted += spent

        pct = (spent / b.monthly_limit * 100) if b.monthly_limit > 0 else 0.0
        remaining = b.monthly_limit - spent

        if spent > b.monthly_limit:
            state = 'danger'
            badge_text = f'Exceeded by {current_user.currency_symbol}{abs(remaining):,.0f}'
        elif pct >= 80:
            state = 'warning'
            badge_text = f'{pct:.0f}% used'
        else:
            state = 'safe'
            badge_text = f'{pct:.0f}% used'

        # Calculate projected spend based on current pace
        daily_spent = spent / max(1, elapsed_days)
        projected = daily_spent * total_days

        budget_items.append({
            'budget': b,
            'category': b.category,
            'limit': b.monthly_limit,
            'spent': spent,
            'remaining': remaining,
            'percentage': round(pct, 1),
            'clamped_pct': min(100.0, round(pct, 1)),
            'state': state,
            'badge_text': badge_text,
            'projected': round(projected, 0)
        })

    # Overall calculation
    overall_pct = (total_spent_budgeted / total_budgeted * 100) if total_budgeted > 0 else 0.0
    total_remaining = total_budgeted - total_spent_budgeted

    # Expense categories available for budget assignment
    categories = get_user_categories(current_user.id, 'expense')
    budgeted_cat_ids = {b.category_id for b in budgets}
    unbudgeted_categories = [c for c in categories if c.id not in budgeted_cat_ids]

    return render_template(
        'budgets.html',
        budget_items=budget_items,
        total_budgeted=total_budgeted,
        total_spent=total_spent_budgeted,
        total_remaining=total_remaining,
        overall_pct=round(overall_pct, 1),
        categories=categories,
        unbudgeted_categories=unbudgeted_categories,
        selected_month=month,
        selected_year=year,
        month_name=calendar.month_name[month],
        remaining_days=remaining_days
    )

@budgets_bp.route('/set', methods=['POST'])
@login_required
def set_budget():
    category_id = request.form.get('category_id', type=int)
    limit_str = request.form.get('monthly_limit', '').strip()
    month = request.form.get('month', date.today().month, type=int)
    year = request.form.get('year', date.today().year, type=int)

    if not category_id or not limit_str:
        flash('Please choose a category and specify a valid limit.', 'danger')
        return redirect(url_for('budgets.index', month=month, year=year))

    try:
        limit = float(limit_str)
        if limit <= 0:
            raise ValueError()
    except ValueError:
        flash('Monthly limit must be a positive number.', 'danger')
        return redirect(url_for('budgets.index', month=month, year=year))

    existing = Budget.query.filter_by(
        user_id=current_user.id,
        category_id=category_id,
        month=month,
        year=year
    ).first()

    if existing:
        existing.monthly_limit = limit
        flash(f'Budget for {existing.category.name} updated to {current_user.currency_symbol}{limit:,.2f}.', 'success')
    else:
        new_budget = Budget(
            user_id=current_user.id,
            category_id=category_id,
            monthly_limit=limit,
            month=month,
            year=year
        )
        db.session.add(new_budget)
        cat = db.session.get(Category, category_id)
        cat_name = cat.name if cat else 'Category'
        flash(f'Budget set for {cat_name}: {current_user.currency_symbol}{limit:,.2f}.', 'success')

    db.session.commit()
    return redirect(url_for('budgets.index', month=month, year=year))

@budgets_bp.route('/<int:budget_id>/delete', methods=['POST'])
@login_required
def delete_budget(budget_id):
    b = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    cat_name = b.category.name if b.category else 'Budget'
    month = b.month
    year = b.year
    db.session.delete(b)
    db.session.commit()
    flash(f'Budget allocation for {cat_name} removed.', 'info')
    return redirect(url_for('budgets.index', month=month, year=year))
