from flask import Flask, render_template, request, redirect
from models import db, Book, Member, Transaction
from datetime import date
import pymysql
import requests

# === Flask App Configuration ===
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Priyanka%4020@localhost:3306/library_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ========== Home Route ==========
@app.route('/')
def index():
    return render_template('index.html')


# ========== BOOK ROUTES ==========
@app.route('/books')
def books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        new_book = Book(
            title=request.form['title'],
            author=request.form['author'],
            isbn=request.form['isbn'],
            publisher=request.form['publisher'],
            pages=int(request.form['pages']),
            stock=int(request.form['stock'])
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect('/books')
    return render_template('add_book.html')

# ========== IMPORT BOOKS FROM API ==========
@app.route('/import_books', methods=['GET', 'POST'])
def import_books():
    if request.method == 'POST':
        title = request.form.get('title', '')
        page = request.form.get('page', 1)

        api_url = f"https://frappe.io/api/method/frappe-library?page={page}"
        if title:
            api_url += f"&title={title}"

        response = requests.get(api_url)
        if response.status_code == 200:
            books = response.json()['message']
            for b in books:
                existing = Book.query.filter_by(isbn=b.get('isbn')).first()
                if not existing:
                    new_book = Book(
                        title=b.get('title', ''),
                        author=b.get('authors', ''),
                        isbn=b.get('isbn', ''),
                        publisher=b.get('publisher', ''),
                        pages=int(b.get('num_pages') or 0),
                        stock=1
                    )
                    db.session.add(new_book)
            db.session.commit()
            return redirect('/books')
        else:
            return "Failed to fetch books from API"
    return render_template('import_books.html')

# ========== MEMBER ROUTES ==========
@app.route('/members')
def members():
    all_members = Member.query.all()
    return render_template('members.html', members=all_members)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        new_member = Member(
            name=request.form['name'],
            contact=request.form['contact']
        )
        db.session.add(new_member)
        db.session.commit()
        return redirect('/members')
    return render_template('add_member.html')


# ========== TRANSACTION ROUTES ==========
@app.route('/transactions')
def transactions():
    all_txns = Transaction.query.all()
    return render_template('transactions.html', transactions=all_txns)

@app.route('/issue', methods=['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        member_id = int(request.form['member_id'])
        book = Book.query.get(book_id)

        if book.stock > 0:
            book.stock -= 1
            txn = Transaction(
                book_id=book_id,
                member_id=member_id,
                issue_date=date.today(),
                rent=0
            )
            db.session.add(txn)
            db.session.commit()
            return redirect('/transactions')
        else:
            return "Book out of stock"

    books = Book.query.all()
    members = Member.query.all()
    return render_template('issue.html', books=books, members=members)

@app.route('/return/<int:txn_id>', methods=['GET', 'POST'])
def return_book(txn_id):
    txn = Transaction.query.get(txn_id)
    if txn.return_date:
        return "Book already returned."

    book = Book.query.get(txn.book_id)
    member = Member.query.get(txn.member_id)

    today = date.today()
    days_borrowed = (today - txn.issue_date).days
    rent_fee = days_borrowed * 5  # ₹5 per day

    txn.return_date = today
    txn.rent = rent_fee

    member.debt += rent_fee
    book.stock += 1

    db.session.commit()
    return redirect('/transactions')

@app.route('/delete_transaction/<int:txn_id>', methods=['GET', 'POST'])
def delete_transaction(txn_id):
    txn = Transaction.query.get_or_404(txn_id)

    # Optional: restore stock if not returned
    if not txn.return_date:
        txn.book.stock += 1

    db.session.delete(txn)
    db.session.commit()
    return redirect('/transactions')


# ========== Run App & Create DB ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
