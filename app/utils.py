import calendar
from datetime import date, datetime, timedelta
from app.models import Category
from app import db

def get_current_month_year():
    today = date.today()
    return today.month, today.year

def get_month_date_range(year=None, month=None):
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month
    _, last_day = calendar.monthrange(year, month)
    return date(year, month, 1), date(year, month, last_day)

def get_previous_month_year(year, month):
    if month == 1:
        return 12, year - 1
    return month - 1, year

def get_user_categories(user_id, category_type=None):
    query = Category.query.filter(
        db.or_(Category.user_id == user_id, Category.user_id.is_(None))
    )
    if category_type:
        query = query.filter_by(type=category_type)
    return query.order_by(Category.name).all()

def format_inr(number):
    try:
        val = float(number)
    except (ValueError, TypeError):
        return f"{number}"
    
    is_negative = val < 0
    val = abs(val)
    
    # Split integer and decimal parts
    parts = f"{val:.2f}".split('.')
    integer_part = parts[0]
    decimal_part = parts[1]
    
    if len(integer_part) > 3:
        last3 = integer_part[-3:]
        remaining = integer_part[:-3]
        # Group remaining digits by 2s from right to left (Indian numbering system)
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ",".join(groups) + "," + last3
    else:
        formatted_int = integer_part
        
    formatted = f"{formatted_int}.{decimal_part}"
    return f"-₹{formatted}" if is_negative else f"₹{formatted}"
