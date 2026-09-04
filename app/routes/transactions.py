import csv
import io
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Transaction, Category
from app.utils import get_user_categories

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('', methods=['GET'])
@login_required
def index():
    # Filter parameters
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', '', type=str)
    tx_type = request.args.get('type', 'all').strip().lower()
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Transaction.query.filter(Transaction.user_id == current_user.id)

    # Search filter
    if search:
        query = query.filter(
            (Transaction.title.ilike(f'%{search}%')) |
            (Transaction.notes.ilike(f'%{search}%')) |
            (Transaction.payment_method.ilike(f'%{search}%'))
        )

    # Category filter
    if category_id and category_id.isdigit():
        query = query.filter(Transaction.category_id == int(category_id))

    # Type filter
    if tx_type in ['income', 'expense']:
        query = query.filter(Transaction.type == tx_type)

    # Date range filters
    if start_date:
        try:
            s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= s_date)
        except ValueError:
            pass

    if end_date:
        try:
            e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= e_date)
        except ValueError:
            pass

    # Sorting
    sort_column = Transaction.date
    if sort_by == 'amount':
        sort_column = Transaction.amount
    elif sort_by == 'title':
        sort_column = Transaction.title

    if sort_order == 'asc':
        query = query.order_by(sort_column.asc(), Transaction.id.asc())
    else:
        query = query.order_by(sort_column.desc(), Transaction.id.desc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    transactions = pagination.items

    # Calculation for filtered set
    filtered_income = sum(t.amount for t in query.all() if t.type == 'income')
    filtered_expense = sum(t.amount for t in query.all() if t.type == 'expense')

    categories = get_user_categories(current_user.id)
    expense_categories = [c for c in categories if c.type == 'expense']
    income_categories = [c for c in categories if c.type == 'income']

    return render_template(
        'transactions.html',
        transactions=transactions,
        pagination=pagination,
        categories=categories,
        expense_categories=expense_categories,
        income_categories=income_categories,
        search=search,
        category_id=category_id,
        tx_type=tx_type,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        filtered_income=filtered_income,
        filtered_expense=filtered_expense,
        total_count=pagination.total
    )

@transactions_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    tx_type = request.form.get('type', 'expense').strip().lower()
    amount_str = request.form.get('amount', '').strip()
    category_id = request.form.get('category_id', type=int)
    date_str = request.form.get('date', '').strip()
    payment_method = request.form.get('payment_method', 'UPI').strip()
    notes = request.form.get('notes', '').strip()

    if not title or not amount_str or not category_id or not date_str:
        flash('Please fill in all mandatory transaction details.', 'danger')
        return redirect(request.referrer or url_for('transactions.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        flash('Amount must be a positive number.', 'danger')
        return redirect(request.referrer or url_for('transactions.index'))

    try:
        tx_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        tx_date = date.today()

    tx = Transaction(
        user_id=current_user.id,
        category_id=category_id,
        title=title,
        type=tx_type,
        amount=amount,
        date=tx_date,
        payment_method=payment_method,
        notes=notes
    )

    db.session.add(tx)
    db.session.commit()
    flash(f'{tx_type.capitalize()} "{title}" for {current_user.currency_symbol}{amount:,.2f} recorded.', 'success')
    return redirect(request.referrer or url_for('transactions.index'))

@transactions_bp.route('/<int:tx_id>/edit', methods=['POST'])
@login_required
def edit(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()

    title = request.form.get('title', '').strip()
    tx_type = request.form.get('type', tx.type).strip().lower()
    amount_str = request.form.get('amount', '').strip()
    category_id = request.form.get('category_id', type=int)
    date_str = request.form.get('date', '').strip()
    payment_method = request.form.get('payment_method', tx.payment_method).strip()
    notes = request.form.get('notes', '').strip()

    if title:
        tx.title = title
    if tx_type in ['income', 'expense']:
        tx.type = tx_type
    if amount_str:
        try:
            val = float(amount_str)
            if val > 0:
                tx.amount = val
        except ValueError:
            pass
    if category_id:
        tx.category_id = category_id
    if date_str:
        try:
            tx.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    tx.payment_method = payment_method
    tx.notes = notes

    db.session.commit()
    flash(f'Transaction "{tx.title}" updated successfully.', 'success')
    return redirect(request.referrer or url_for('transactions.index'))

@transactions_bp.route('/<int:tx_id>/delete', methods=['POST'])
@login_required
def delete(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    title = tx.title
    db.session.delete(tx)
    db.session.commit()
    flash(f'Transaction "{title}" deleted.', 'info')
    return redirect(request.referrer or url_for('transactions.index'))

@transactions_bp.route('/export-csv', methods=['GET'])
@login_required
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Type', 'Title', 'Category', 'Amount', 'Payment Method', 'Notes'])

    txs = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    for t in txs:
        writer.writerow([
            t.id,
            t.date.strftime('%Y-%m-%d'),
            t.type,
            t.title,
            t.category.name if t.category else 'Unknown',
            t.amount,
            t.payment_method,
            t.notes or ''
        ])

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=SmartExpense_Transactions_{date.today()}.csv'
    return response

@transactions_bp.route('/import-csv', methods=['POST'])
@login_required
def import_csv():
    if 'file' not in request.files:
        flash('No file uploaded.', 'danger')
        return redirect(url_for('transactions.index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('transactions.index'))

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8-sig'), newline=None)
        reader = csv.DictReader(stream)
        imported_count = 0

        # Pre-fetch category mapping
        cats = get_user_categories(current_user.id)
        cat_map = {c.name.lower(): c.id for c in cats}
        default_exp_cat = next((c.id for c in cats if c.type == 'expense'), None)
        default_inc_cat = next((c.id for c in cats if c.type == 'income'), None)

        for row in reader:
            title = row.get('Title') or row.get('title') or row.get('Description') or 'Imported Item'
            tx_type = (row.get('Type') or row.get('type') or 'expense').lower().strip()
            amount_val = float(row.get('Amount') or row.get('amount') or 0.0)
            date_raw = row.get('Date') or row.get('date') or date.today().strftime('%Y-%m-%d')

            try:
                tx_date = datetime.strptime(date_raw.strip(), '%Y-%m-%d').date()
            except ValueError:
                tx_date = date.today()

            cat_raw = (row.get('Category') or row.get('category') or '').strip().lower()
            cat_id = cat_map.get(cat_raw)
            if not cat_id:
                cat_id = default_inc_cat if tx_type == 'income' else default_exp_cat

            payment = row.get('Payment Method') or row.get('PaymentMethod') or 'Imported'
            notes = row.get('Notes') or ''

            tx = Transaction(
                user_id=current_user.id,
                category_id=cat_id,
                title=title,
                type=tx_type,
                amount=abs(amount_val),
                date=tx_date,
                payment_method=payment,
                notes=notes
            )
            db.session.add(tx)
            imported_count += 1

        db.session.commit()
        flash(f'Successfully imported {imported_count} transactions!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error parsing CSV file: {str(e)}', 'danger')

    return redirect(url_for('transactions.index'))
