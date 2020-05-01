import os
import psycopg2
import requests

from flask import Flask, session, render_template, request, jsonify, redirect, abort, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Flask Sessions secret key. Keep Secret because it is a secret.
app.secret_key = b'5)\x91\x15{\xc3\xa9o\x91\x95\xa9\xdc{\xb4V\xbd'


# Set database env for Heroku
DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
	books = db.execute("SELECT * FROM books").fetchall()
	
	# Check if user is logged in
	if 'user' in session:
		return render_template('index.html', books=books)
	return render_template('login.html')
	

@app.route("/login", methods=['POST', 'GET'])
def login():

	if request.method == "GET":
		return render_template('login.html')
			
	elif request.method == "POST":
	
		username = request.form.get('username')
		password = request.form.get('password')
		
		user = db.execute("SELECT * FROM users WHERE username = :username", {"username":username})
		
		# Check username against database.
		if user.rowcount == 0:
			return render_template('error.html', message="Please Create an account, we do not have a record of that username. Check spelling if you believe this was a mistake.")
		
		# If username is in database.
		elif user.rowcount == 1:
			
			# retrive database password and check hash.
			data_password = db.execute("SELECT password FROM users WHERE username = :username", {"username":username}).fetchone()[0]
			check_hash = check_password_hash(data_password, password)
		
			# make sure password matches
			if check_hash == False:
				return render_template('error.html', message="Password does not match.")
		
			# hash matches password
			elif check_hash == True:
				session ['user'] = request.form['username']
				return redirect(url_for('index'))
			
			# Other issues
			else:
				return render_template('error.html', message="It like something went wrong, please try again")
				
		# Any other issues.
		else:
			return render_template('error.html', message="It looks like something went wrong, please try again")
			
		
@app.route("/signup", methods=['POST', 'GET'])
def signup():

	if request.method == "GET":
		return render_template('signup.html')
			
	elif request.method == "POST":
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
		username = request.form.get('username')
		password = request.form.get('password')
		password_hash = generate_password_hash(request.form.get('password'), "sha256")
		
		# See if user name or password is already created
		if db.execute("SELECT * FROM users WHERE username = :username OR password = :password OR first_name = :first_name OR last_name = :last_name", {"username":username, "password":password_hash, "first_name":first_name, "last_name":last_name}).rowcount > 0:
			return login()
		
		# create new user with the form data.
		else:
			db.execute("INSERT INTO users (first_name, last_name, username, password) VALUES (:first_name, :last_name, :username, :password)", {"first_name": first_name, "last_name": last_name, "username": username, "password": password_hash})
			db.commit()
		return index()
	
	
@app.route("/logout")
def logout():
	# remove username from session.
	session.pop('user', None)
	return index()
	
	
@app.route("/search", methods=['GET', 'POST'])
def search():
	if request.method == "GET":
		return index()
		
	elif request.method == "POST":
		search = request.form['search']
		search_escape = '%' + search + '%'

		# search by title, author, ISBN
		data = db.execute("SELECT * from books WHERE UPPER(title) LIKE UPPER(:search) OR UPPER(author) LIKE UPPER(:search) OR UPPER(isbn) LIKE UPPER (:search)", {"search": search_escape})
		db.commit()
		results = data.fetchall()

		# all in the search box will return all the books
		if len(results) == 0 and search == 'all':
			all_data=db.execute("SELECT * from books")
			results = all_data.fetchall()
			
		elif len(results) == 0:
			return render_template("error.html", message="We are sorry, your search came up with no results")
            
		else:
			return render_template("books.html", books=results)
    
    
    
@app.route("/books")
def books():

	# Page is technically availible without login.
	books = db.execute("SELECT * FROM books").fetchall()
	return render_template("books.html", books=books)


@app.route("/book/<int:book_id>")
def book(book_id):
	
	# Check if user is logged in
	if 'user' not in session:
		return index()
	
	# Make sure book exists
	book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
	if book is None:
		return render_template("error.html", message="No such book")
		
	# Get Reviews for Book
	review = db.execute("SELECT reviews, stars, first_name FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
	
	# Get Goodreads Data
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "rUuhDWjh4OfyuYmcQIwQQ", "isbns": book.isbn})
		
	# Goodreads Success?
	if res.status_code != 200:
		total_ratings = 0
		average_rating = 0
		
	else:
		data = res.json()
		total_ratings = data["books"][0]["work_ratings_count"]
		average_rating = data["books"][0]["average_rating"]
		    
	return render_template("book.html", book=book, review=review, total_ratings=total_ratings, average_rating=average_rating)
	

@app.route("/review/<int:book_id>", methods=["POST"])
def review(book_id):
	"""Review a Book."""
	
	# Get form information
	review = request.form.get("review")
	stars = request.form.get("stars")
	username = session['user']
	user_id = db.execute("SELECT id FROM users WHERE username = :username", {"username":username}).fetchone()[0]
	
	
	# Make sure book exists.
	if db.execute("SELECT * FROM books WHERE id = :id", {"id":book_id}).rowcount == 0:
		return render_template ("error.html", message="No such book with that id.")
	
	# Check if reviewed
	if db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {"user_id":user_id, "book_id":book_id}).rowcount > 0:
		return render_template ("error.html", message="You have already reviewed this book, sorry! Try reviewing another!")
	
	db.execute("INSERT INTO reviews (user_id, reviews, book_id, stars) VALUES (:user_id, :reviews, :book_id, :stars)", {"user_id": user_id, "reviews": review, "book_id": book_id, "stars": stars})
	db.commit()
	return render_template("success.html")
	
	
@app.errorhandler(404)
def page_not_found(error):
	return render_template('error.html', message="404 error, page not found")
	
	
@app.route("/api/book/<string:isbn>")
def book_api(isbn):
	
	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

	if book is None:
		return jsonify({"error": "Invalid isbn"}), 404
	
	# Make sure book exists
	book_id = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()[0]
	
	# Get reviews
	reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id":book_id})
	how_many_reviews = reviews.rowcount
	stars = db.execute("SELECT AVG(stars) FROM reviews WHERE book_id = :book_id", {"book_id":book_id}).fetchone()[0]
	
	
	return jsonify({
			"title": book.title,
			"author": book.author,
			"year": book.year,
			"isbn": book.isbn,
			"review_count": how_many_reviews,
			"average_score": stars})
