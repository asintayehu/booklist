# Core dependencies
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initializing app, database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"
db = SQLAlchemy(app)

class Book():
    id = db.Column(db.Integer, primary_key=True)
    title = db.column(db.String(100), nullable=False)
    author = db.column(db.String(100), nullable=False)
    genre = db.column(db.String(100), nullable=True)

# estbalish routes
@app.route('/')
def index():
    return 'Hello World!'

if __name__ == "__main__":
    app.run(debug=True)