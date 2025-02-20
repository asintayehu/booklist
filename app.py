# Core dependencies
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import *

# Initializing app, database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"
db = SQLAlchemy(app)

class Book():
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default= lambda : datetime.now(timezone.utc))

# estbalish routes
@app.route('/')
def index():
    if request.method == 'POST':
        book_title = request.form['add-book-name']

    else:
        return render_template('index.html')
    
    # want attribute and wanna add that to the 
    # table or at least display it on the page in raw html

if __name__ == "__main__":
    app.run(debug=True)