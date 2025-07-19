from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    author = db.Column(db.String(100))
    isbn = db.Column(db.String(50))
    publisher = db.Column(db.String(100))
    pages = db.Column(db.Integer)
    stock = db.Column(db.Integer)

    transactions = db.relationship('Transaction', backref='book')

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    debt = db.Column(db.Float, default=0.0)

    transactions = db.relationship('Transaction', backref='member')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    issue_date = db.Column(db.Date)
    return_date = db.Column(db.Date, nullable=True)
    rent = db.Column(db.Float)
