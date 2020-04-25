import os
import psycopg2

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

#set database env
DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

#Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
	books = db.execute("SELECT * FROM books").fetchall()
	return render_template("index.html", books=books)
	
#@app.route("/book/<int:book_id", methods=["POST"])
#def book_details():
#	"""Book details"""
	
	
	
@app.route("/books")
def books():
    """Lists 20 books."""
    books = db.execute("SELECT * FROM books LIMIT 20").fetchall()
    return render_template("books.html", books=books)


