# Core dependencies
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import *
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate

# Initializing app, database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bookie.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False, default="")
    genre = db.Column(db.String(100), nullable=True, default="")
    date_created = db.Column(db.DateTime, default= lambda : datetime.now(timezone.utc))

    def __repr__(self):
        return '<Book %r>' % self.id


# estbalish routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        book_title = request.form.get('book')
        new_book = Book(title=book_title)

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
        return render_template('index.html', book_list=Books)
    
    # want attribute and wanna add that to the 
    # table or at least display it on the page in raw html

if __name__ == "__main__":
    app.run(debug=True)