import os
import psycopg2

from flask import Flask, session, render_template, request, redirect, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

#flask sessions secret key
#app.secret_key = b'5)\x91\x15{\xc3\xa9o\x91\x95\xa9\xdc{\xb4V\xbd'


#set database env for Heroku
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

signed_in = []

@app.route("/")
def index():
	if not session.get('signed_in'):
		return render_template('login.html')
	else:
		books = db.execute("SELECT * FROM books").fetchall()
		return render_template('index.html', books=books)
			
			
@app.route("/review", methods=["POST"])
def review():
	"""Review a Book."""
	
	# Get form information
	review = request.form.get("review")
	try:
		book_id = int(request.form.get("book_id"))
	except ValueError:
		return render_template("error.html", message="This is not a valid book")
		
	# Make sure book exists.
	if db.execute("SELECT * FROM books WHERE id = :id", {"id":book_id}).rowcount == 0:
		return render_template ("error.html", message="No such book with that id.")
	db.execute("INSERT INTO reviews (user_id, review, book_id) VALUES (:user_id, :review, :book_id)", {"user_id": user_id, "review": review, "book_id": book_id})
	db.commit()
	return render_template("success.html")


@app.route("/login", methods=['POST'])
def login():
	
	username = request.form.get('username')
	password = request.form.get('password')
	
	user = db.execute("SELECT * FROM users WHERE username = :username", {"username":username})
	p_check = db.execute("SELECT * FROM users WHERE password = :password", {"password":password})
	
	
	if user.rowcount == 0:
		return render_template('error.html', message="Please Create an account.")
		
	else:
		session ['signed_in'] = True
		return index()
		
		
@app.route("/signup", methods=["POST"])
def signup():

	first_name = request.form.get('first_name')
	last_name = request.form.get('last_name')
	username = request.form.get('username')
	password = request.form.get('password')
	
	
	
	if user:
		return redirect(url_for('signup'))
	
	# create new user with the form data. Hash the password so plaintext version isn't save.
	db.execute("INSERT INTO users (first_name, last_name, username, password) VALUES (:first_name, :last_name, :username, :password)", {"first_name": f_name, "lat_name": l_name, "username": username, "password": password})
	db.session.commit()
	
	return redirect(url_for('login'))
	
@app.route("/logout")
def logout():
	session['signed_in'] = False
	return index()
