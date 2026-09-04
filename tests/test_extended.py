import unittest
from datetime import date
from app import create_app, db
from app.models import User, Category, Transaction, Budget

class ExtendedSmartExpenseTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        self.user = User(
            username='tejas',
            email='tejas@smartexpense.com',
            full_name='Tejas Sharma'
        )
        self.user.set_password('admin123')
        db.session.add(self.user)
        db.session.commit()

        # Login client
        self.client.post('/login', data={
            'identifier': 'tejas',
            'password': 'admin123'
        })
        self.cat = Category.query.filter_by(name='Food & Dining').first()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_full_transaction_flow(self):
        # 1. Add Transaction
        res = self.client.post('/transactions/add', data={
            'title': 'Test Grocery',
            'type': 'expense',
            'amount': '1250.00',
            'category_id': self.cat.id,
            'date': '2026-09-02',
            'payment_method': 'UPI',
            'notes': 'Supermarket run'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        tx = Transaction.query.filter_by(title='Test Grocery').first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.amount, 1250.00)

        # 2. Edit Transaction
        res = self.client.post(f'/transactions/{tx.id}/edit', data={
            'title': 'Test Grocery Updated',
            'type': 'expense',
            'amount': '1350.00',
            'category_id': self.cat.id,
            'date': '2026-09-02',
            'payment_method': 'UPI',
            'notes': 'Updated notes'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        tx = db.session.get(Transaction, tx.id)
        self.assertEqual(tx.title, 'Test Grocery Updated')
        self.assertEqual(tx.amount, 1350.00)

        # 3. Delete Transaction
        res = self.client.post(f'/transactions/{tx.id}/delete', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(db.session.get(Transaction, tx.id))

    def test_budget_flow(self):
        # Set Budget
        res = self.client.post('/budgets/set', data={
            'category_id': self.cat.id,
            'monthly_limit': '8000.00',
            'month': 9,
            'year': 2026
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        b = Budget.query.filter_by(user_id=self.user.id, category_id=self.cat.id).first()
        self.assertIsNotNone(b)
        self.assertEqual(b.monthly_limit, 8000.00)

        # Delete Budget
        res = self.client.post(f'/budgets/{b.id}/delete', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(db.session.get(Budget, b.id))

    def test_csv_export(self):
        res = self.client.get('/transactions/export-csv')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'text/csv')

if __name__ == '__main__':
    unittest.main()
