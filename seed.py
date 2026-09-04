import os
from datetime import date, datetime, timedelta
from app import create_app, db
from app.models import User, Category, Transaction, Budget

def seed_demo_data_for_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return

    # Remove existing user transactions and budgets to seed fresh clean data
    Transaction.query.filter_by(user_id=user.id).delete()
    Budget.query.filter_by(user_id=user.id).delete()

    cats = {c.name: c for c in Category.query.filter(
        db.or_(Category.user_id == user.id, Category.user_id.is_(None))
    ).all()}

    # Reference today's date or September 2026
    today = date.today()
    cur_year = today.year
    cur_month = today.month

    # Calculate previous months
    if cur_month == 1:
        prev_m1, prev_y1 = 12, cur_year - 1
        prev_m2, prev_y2 = 11, cur_year - 1
    elif cur_month == 2:
        prev_m1, prev_y1 = 1, cur_year
        prev_m2, prev_y2 = 12, cur_year - 1
    else:
        prev_m1, prev_y1 = cur_month - 1, cur_year
        prev_m2, prev_y2 = cur_month - 2, cur_year

    # Helper to add transaction
    def add_tx(title, cat_name, tx_type, amount, tx_date, payment='UPI', notes=''):
        cat = cats.get(cat_name)
        if not cat:
            cat = Category.query.filter_by(type=tx_type).first()
        t = Transaction(
            user_id=user.id,
            category_id=cat.id,
            title=title,
            type=tx_type,
            amount=float(amount),
            date=tx_date,
            payment_method=payment,
            notes=notes
        )
        db.session.add(t)

    # 1. Current Month (e.g. Sep 2026) Transactions
    # Income: ₹50,000 Salary
    add_tx('Monthly Tech Salary', 'Salary', 'income', 50000.0, date(cur_year, cur_month, 1), 'Bank Transfer', 'Direct payroll credit')
    
    # Expenses matching user's exact specification (~₹21,450 total):
    # Food: ₹5,200
    add_tx('Supermarket & Grocery', 'Food & Dining', 'expense', 1250.0, date(cur_year, cur_month, min(2, today.day)), 'UPI', 'Weekly provisions')
    add_tx('Gourmet Dinner with Friends', 'Food & Dining', 'expense', 2450.0, date(cur_year, cur_month, min(3, today.day)), 'Credit Card', 'Weekend Italian dinner')
    add_tx('Swiggy Office Lunches', 'Food & Dining', 'expense', 1500.0, date(cur_year, cur_month, min(4, today.day)), 'UPI', 'Meal box delivery')
    
    # Travel: ₹4,550 (91% of 5,000 budget!)
    add_tx('Uber Commute to Office', 'Transportation & Travel', 'expense', 350.0, date(cur_year, cur_month, min(1, today.day)), 'UPI', 'Morning peak ride')
    add_tx('Fuel Petrol Fill-up', 'Transportation & Travel', 'expense', 2200.0, date(cur_year, cur_month, min(2, today.day)), 'Credit Card', 'Full tank fuel')
    add_tx('Airport Cab & Tolls', 'Transportation & Travel', 'expense', 2000.0, date(cur_year, cur_month, min(3, today.day)), 'UPI', 'Expressway travel')

    # Shopping: ₹4,650 (Exceeds ₹4,000 budget by ₹650!)
    add_tx('Zara Casual Shirts', 'Shopping & Lifestyle', 'expense', 3200.0, date(cur_year, cur_month, min(2, today.day)), 'Credit Card', 'Autumn wardrobe')
    add_tx('Amazon Electronics Cable', 'Shopping & Lifestyle', 'expense', 1450.0, date(cur_year, cur_month, min(3, today.day)), 'UPI', 'USB-C fast charger')

    # Entertainment: ₹1,450
    add_tx('Netflix 4K Premium', 'Entertainment', 'expense', 649.0, date(cur_year, cur_month, 1), 'Credit Card', 'Auto-renew monthly sub')
    add_tx('PVR IMAX Movie Tickets', 'Entertainment', 'expense', 801.0, date(cur_year, cur_month, min(3, today.day)), 'UPI', 'Weekend cinema')

    # Bills & Utilities: ₹3,800
    add_tx('Airtel High-Speed Fiber', 'Bills & Utilities', 'expense', 1179.0, date(cur_year, cur_month, min(1, today.day)), 'UPI', 'Broadband internet')
    add_tx('Electricity Discom Bill', 'Bills & Utilities', 'expense', 2621.0, date(cur_year, cur_month, min(2, today.day)), 'Net Banking', 'Monthly electricity bill')

    # Healthcare: ₹1,800
    add_tx('Health Insurance & Pharmacy', 'Healthcare & Wellness', 'expense', 1800.0, date(cur_year, cur_month, min(3, today.day)), 'UPI', 'Health supplement stack')

    # Total Sep Expense: 1250+2450+1500 + 350+2200+2000 + 3200+1450 + 649+801 + 1179+2621 + 1800 = 21,450!
    # Net Savings = 50,000 - 21,450 = 28,550 (57.1% savings rate!)

    # 2. Previous Month (Month - 1)
    # Income: ₹48,000 | Expense: ₹22,150 | Savings: ₹25,850 (53.8%)
    add_tx('Monthly Tech Salary', 'Salary', 'income', 48000.0, date(prev_y1, prev_m1, 1), 'Bank Transfer')
    add_tx('Grocery Basket', 'Food & Dining', 'expense', 4200.0, date(prev_y1, prev_m1, 5), 'UPI')
    add_tx('Fuel & Transit', 'Transportation & Travel', 'expense', 3800.0, date(prev_y1, prev_m1, 8), 'Credit Card')
    add_tx('Myntra Shopping', 'Shopping & Lifestyle', 'expense', 3900.0, date(prev_y1, prev_m1, 12), 'Credit Card')
    add_tx('Subscriptions & Movies', 'Entertainment', 'expense', 2100.0, date(prev_y1, prev_m1, 15), 'UPI')
    add_tx('Utilities & Power', 'Bills & Utilities', 'expense', 4150.0, date(prev_y1, prev_m1, 18), 'Net Banking')
    add_tx('Dental Checkup', 'Healthcare & Wellness', 'expense', 4000.0, date(prev_y1, prev_m1, 22), 'UPI')

    # 3. Two Months Prior (Month - 2)
    # Income: ₹46,000 | Expense: ₹24,000 | Savings: ₹22,000 (47.8%)
    add_tx('Monthly Tech Salary', 'Salary', 'income', 46000.0, date(prev_y2, prev_m2, 1), 'Bank Transfer')
    add_tx('Food & Provisions', 'Food & Dining', 'expense', 5600.0, date(prev_y2, prev_m2, 4), 'UPI')
    add_tx('Commute & Petrol', 'Transportation & Travel', 'expense', 4200.0, date(prev_y2, prev_m2, 10), 'Credit Card')
    add_tx('Home Essentials', 'Shopping & Lifestyle', 'expense', 5200.0, date(prev_y2, prev_m2, 14), 'UPI')
    add_tx('Concert & Leisure', 'Entertainment', 'expense', 3500.0, date(prev_y2, prev_m2, 19), 'Credit Card')
    add_tx('Power & Water', 'Bills & Utilities', 'expense', 3500.0, date(prev_y2, prev_m2, 24), 'Net Banking')
    add_tx('Books & Course', 'Education & Books', 'expense', 2000.0, date(prev_y2, prev_m2, 28), 'UPI')

    # 4. Seed User's Budgets for Current Month
    budget_allocations = [
        ('Food & Dining', 8000.0),       # Spent: 5,200 (65%)
        ('Transportation & Travel', 5000.0), # Spent: 4,550 (91% - Trigger Warning!)
        ('Shopping & Lifestyle', 4000.0), # Spent: 4,650 (Exceeded by ₹650 - Trigger Exceeded Alert!)
        ('Entertainment', 2000.0),       # Spent: 1,450 (72.5%)
        ('Bills & Utilities', 6000.0),   # Spent: 3,800 (63.3%)
        ('Healthcare & Wellness', 3000.0)# Spent: 1,800 (60%)
    ]

    for cat_name, limit in budget_allocations:
        cat = cats.get(cat_name)
        if cat:
            b = Budget(
                user_id=user.id,
                category_id=cat.id,
                monthly_limit=limit,
                month=cur_month,
                year=cur_year
            )
            db.session.add(b)

    db.session.commit()
    print(f'Successfully seeded demo financial data for {user.full_name} ({user.email})!')

def seed_all():
    app = create_app('default')
    with app.app_context():
        # Check or create default demo user: Tejas
        user = User.query.filter_by(username='tejas').first()
        if not user:
            user = User(
                username='tejas',
                email='tejasprataps891@gmail.com',
                full_name='Tejas Pratap Singh',
                currency_symbol='₹',
                monthly_income_target=50000.0
            )
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()
            print('Created demo user: tejasprataps891@gmail.com / admin123')

        seed_demo_data_for_user(user.id)

if __name__ == '__main__':
    seed_all()
