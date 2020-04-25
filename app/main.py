import os
import boto

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from boto.s3.connection import S3Connection
s3 = S3Connection(os.environ['1357'], os.environ['246810'])

app = Flask(__name__)


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
	return render_template("index.html")
	
@app.route("/books")
def books():
    """Lists 20 books."""
    books = db.execute("SELECT * FROM books LIMIT 20").fetchall()
    return render_template("books.html", books=books)
