# Core dependencies
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import *
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
import requests as rq
import secrets
from wtforms import Form, BooleanField, StringField, validators, IntegerField, SubmitField, PasswordField, ValidationError
import os
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user

# Initializing app, database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bookie.db"
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

# iterator list
numbers = list(range(0,30))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    bookshelf = db.relationship('Book', backref='User', lazy='dynamic')

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(user_name=username).first()
        if user and user.password == password:
            return user
        return None

    def __repr__(self):
        return '<Username: %s>' % self.id


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False, default="")
    genre = db.Column(db.String(100), nullable=True, default="")
    date_created = db.Column(db.DateTime, default= lambda : datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Double, nullable=False)

    __table_args__ = (
        db.CheckConstraint('rating BETWEEN 1 AND 5', name='rating_range'),
    )

    def __repr__(self):
        return '<Book %r>' % self.id

class RegistrationForm(FlaskForm):
    # Enter username, password.
    username = StringField('Username', validators=[validators.Length(min=6, max=20)])
    password = PasswordField('Password', validators=[validators.Length(min=8,max=50)])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    # Enter username, password.
    username = StringField('Username', validators=[validators.Length(min=6, max=20)])
    password = PasswordField('Password', validators=[validators.Length(min=8,max=50)])
    submit = SubmitField("Login")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def url_has_allowed_host_and_scheme(url, host):
    if not url:
        return False
    parsed_url = url_parse(url)
    return parsed_url.scheme in ('http', 'https') and parsed_url.netloc == host


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        print("Received form data:", request.form)  # Debugging
        print("Form validation:", form.validate_on_submit())  # Debugging
        print("Form errors:", form.errors)  # Debugging
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            login_user(user)
            flash('Logged in successfully!')
            next_page = request.form.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        existing_name = User.query.filter_by(user_name=username).first()
        if existing_name:
            flash('Username already taken, please choose another one.', 'error')
            return render_template('register.html', form=form)
        else:
            try:
                user = User(user_name=username, password=password)
                db.session.add(user)
                db.session.commit()
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                print("Error:", e)

    return render_template('register.html', form=form)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Creation of books
        book_title = request.form.get('book')
        book_author = request.form.get('author')
        book_genre = request.form.get('genre')
        book_rating = request.form.get('rating')
        owner_id= current_user.id
        username = User.query.filter_by(id=owner_id).first().user_name
        new_book = Book(title=book_title, author=book_author, genre=book_genre, rating=book_rating, owner_id=owner_id)
        try:
            db.session.add(new_book)
            db.session.commit()
            # Query the database
            Books = Book.query.order_by(Book.date_created).all()
            return redirect(url_for('index'))
        except Exception as e:
            return f'{str(e)}'
    else:
        owner_id= current_user.id
        username = User.query.filter_by(id=owner_id).first().user_name
        Books = Book.query.order_by(Book.date_created).all()
        return render_template('index.html',   packed=zip(Books, numbers), username=username)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

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
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/add-notes/<int:id>', methods=['GET', 'POST'])
def update(id):
    
    book = db.get_or_404(Book, id)
    if request.method == 'POST':
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