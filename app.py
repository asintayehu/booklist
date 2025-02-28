# Core dependencies
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import *
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
import requests as rq
from flask_login import LoginManager, UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import secrets

# Initializing app, database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bookie.db"
app.config['SECRET_KEY'] = ''
login_manager = LoginManager()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager.init_app(app)
login_manager.login_view = "login"

# iterator list
numbers = list(range(0,30))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    bookshelf = db.relationship('Book', backref='User', lazy='dynamic')

    # is_authenticated
    # is_active
    # is_anonymous
    # get_id

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

class RegisterForm(FlaskForm):
    user_name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    # Query database
    def validate_name(self, user_name):
        with app.app_context():
            existing_name = User.query.filter_by(user_name=user_name.data).first()
            if existing_name:
                raise ValidationError ("User already exists")

    # existing_name = User.query.filter_by(user_name=user_name.data).first()
    # if existing_name:
    #     raise ValidationError ("User already exists")
    
class LoginForm(FlaskForm):
    user_name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.user_name.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(user_name=form.user_name.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)