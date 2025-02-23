# Core dependencies
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import *
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
import requests as rq

# Initializing app, database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bookie.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# iterator list
numbers = list(range(0,30))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False, default="")
    genre = db.Column(db.String(100), nullable=True, default="")
    date_created = db.Column(db.DateTime, default= lambda : datetime.now(timezone.utc))
    rating = db.Column(db.Double, nullable=False)

    __table_args__ = (
        db.CheckConstraint('rating BETWEEN 1 AND 5', name='rating_range'),
    )

    def __repr__(self):
        return '<Book %r>' % self.id


# estbalish routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Creation of books
        book_title = request.form.get('book')
        book_author = request.form.get('author')
        book_genre = request.form.get('genre')
        book_rating = request.form.get('rating')
        new_book = Book(title=book_title, author=book_author, genre=book_genre, rating=book_rating)

        # # String parser
        # cleaned_title = new_book.title.replace(" ", "+").lower()
        # # convert to lower case and replace all spaces with a +


        # url = f'https://openlibrary.org/search.json?q={cleaned_title}'
        # book_request = rq.get(url)
        # print(book_request.json())
        

        try:
            db.session.add(new_book)
            db.session.commit()

            # Query the database
            Books = Book.query.order_by(Book.date_created).all()
            return redirect(url_for('index'))
        except Exception as e:
            return f'{str(e)}'

    else:
        Books = Book.query.order_by(Book.date_created).all()
        return render_template('index.html',   packed=zip(Books, numbers))


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    if request.method == 'POST':
        # Grab id for book
        target_book = db.get_or_404(Book, id)

        try:
            db.session.delete(target_book)
            db.session.commit()
        except Exception as e:
            return f'{str(e)}'
        return redirect('/')
    else:
        return redirect('/')

@app.route('/add-notes/<int:id>', methods=['GET', 'POST'])
def update(id):
    
    book = db.get_or_404(Book, id)
    if request.method == 'POST':
        # Query database and then grab all elements by ID
        # Want to be able to edit date started and rating
        book.rating = request.form.get('rating')
    else:
        return render_template('update.html', id=id, book=book)

    try:
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f'{str(e)}'



if __name__ == "__main__":
    app.run(debug=True)