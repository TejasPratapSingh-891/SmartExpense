from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    currency_symbol = db.Column(db.String(10), default='₹', nullable=False)
    monthly_income_target = db.Column(db.Float, default=50000.0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True) # None = System Default
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(10), default='expense', nullable=False) # 'expense' or 'income'
    icon = db.Column(db.String(50), default='tag', nullable=False)
    color = db.Column(db.String(20), default='#6366F1', nullable=False)

    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy='dynamic')
    budgets = db.relationship('Budget', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'icon': self.icon,
            'color': self.color,
            'is_custom': self.user_id is not None
        }

    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(10), nullable=False, index=True) # 'income' or 'expense'
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    payment_method = db.Column(db.String(50), default='UPI', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Unknown',
            'category_icon': self.category.icon if self.category else 'tag',
            'category_color': self.category.color if self.category else '#6366F1',
            'title': self.title,
            'type': self.type,
            'amount': self.amount,
            'date': self.date.strftime('%Y-%m-%d'),
            'payment_method': self.payment_method,
            'notes': self.notes or ''
        }

    def __repr__(self):
        return f'<Transaction {self.title} ({self.type}: {self.amount})>'


class Budget(db.Model):
    __tablename__ = 'budgets'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'category_id', 'month', 'year', name='unique_user_cat_month_year'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False) # 1-12
    year = db.Column(db.Integer, nullable=False)  # 2026
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Unknown',
            'category_icon': self.category.icon if self.category else 'tag',
            'category_color': self.category.color if self.category else '#6366F1',
            'monthly_limit': self.monthly_limit,
            'month': self.month,
            'year': self.year
        }

    def __repr__(self):
        return f'<Budget Category={self.category_id} Limit={self.monthly_limit} ({self.month}/{self.year})>'
