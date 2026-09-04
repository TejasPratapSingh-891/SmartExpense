import unittest
from datetime import date
from app import create_app, db
from app.models import User, Category, Transaction, Budget
from app.services.analytics_service import get_monthly_kpis, get_spending_by_category
from app.services.health_score import calculate_financial_health_score
from app.services.insights_engine import generate_smart_insights

class SmartExpenseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Create test user
        self.user = User(
            username='testtejas',
            email='test@smartexpense.com',
            full_name='Tejas Sharma',
            currency_symbol='?',
            monthly_income_target=50000.0
        )
        self.user.set_password('secure123')
        db.session.add(self.user)
        db.session.commit()

        # Fetch default categories
        self.cat_salary = Category.query.filter_by(name='Salary', type='income').first()
        self.cat_food = Category.query.filter_by(name='Food & Dining', type='expense').first()
        self.cat_travel = Category.query.filter_by(name='Transportation & Travel', type='expense').first()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        self.assertTrue(self.user.check_password('secure123'))
        self.assertFalse(self.user.check_password('wrongpass'))

    def test_transaction_crud(self):
        # Create income
        inc = Transaction(
            user_id=self.user.id,
            category_id=self.cat_salary.id,
            title='Monthly Salary',
            type='income',
            amount=50000.0,
            date=date(2026, 9, 1),
            payment_method='Bank Transfer'
        )
        # Create expense
        exp = Transaction(
            user_id=self.user.id,
            category_id=self.cat_food.id,
            title='Groceries',
            type='expense',
            amount=2500.0,
            date=date(2026, 9, 2),
            payment_method='UPI'
        )
        db.session.add_all([inc, exp])
        db.session.commit()

        # Verify query
        txs = Transaction.query.filter_by(user_id=self.user.id).all()
        self.assertEqual(len(txs), 2)

        # Verify KPIs
        kpis = get_monthly_kpis(self.user.id, 2026, 9)
        self.assertEqual(kpis['income'], 50000.0)
        self.assertEqual(kpis['expense'], 2500.0)
        self.assertEqual(kpis['net_savings'], 47500.0)
        self.assertEqual(kpis['savings_rate'], 95.0)

    def test_budget_threshold_and_health_score(self):
        # Set budget limit
        budget = Budget(
            user_id=self.user.id,
            category_id=self.cat_food.id,
            monthly_limit=5000.0,
            month=9,
            year=2026
        )
        db.session.add(budget)

        # Add income and expense
        inc = Transaction(
            user_id=self.user.id,
            category_id=self.cat_salary.id,
            title='Salary',
            type='income',
            amount=50000.0,
            date=date(2026, 9, 1)
        )
        exp = Transaction(
            user_id=self.user.id,
            category_id=self.cat_food.id,
            title='Dining Out',
            type='expense',
            amount=4200.0,  # 84% utilized -> trigger warning!
            date=date(2026, 9, 3)
        )
        db.session.add_all([inc, exp])
        db.session.commit()

        # Test Insights
        insights = generate_smart_insights(self.user.id, 2026, 9)
        self.assertTrue(any('used' in ins['message'] or '84%' in ins['title'] for ins in insights))

        # Test Health Score
        score = calculate_financial_health_score(self.user.id, 2026, 9)
        self.assertGreaterEqual(score['score'], 0)
        self.assertLessEqual(score['score'], 100)
        self.assertIn(score['grade'], ['Excellent', 'Good', 'Fair', 'Needs Attention'])

    def test_routes_smoke(self):
        # Test landing page
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

        # Test login page
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)

        # Test login action
        res = self.client.post('/login', data={
            'identifier': 'testtejas',
            'password': 'secure123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Tejas', res.data)

        # Test authenticated dashboard
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)

        # Test transactions page
        res = self.client.get('/transactions')
        self.assertEqual(res.status_code, 200)

        # Test budgets page
        res = self.client.get('/budgets')
        self.assertEqual(res.status_code, 200)

        # Test analytics page
        res = self.client.get('/analytics')
        self.assertEqual(res.status_code, 200)

        # Test reports page
        res = self.client.get('/reports')
        self.assertEqual(res.status_code, 200)

        # Test settings page
        res = self.client.get('/settings')
        self.assertEqual(res.status_code, 200)

        # Test API endpoint
        res = self.client.get('/api/dashboard/chart-data')
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
