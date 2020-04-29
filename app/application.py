import os
import psycopg2

from flask import Flask, session, render_template, request, redirect, abort, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from markupsafe import escape


app = Flask(__name__)

# Flask Sessions secret key. Keep Secret because it is a secret.
app.secret_key = b'5)\x91\x15{\xc3\xa9o\x91\x95\xa9\xdc{\xb4V\xbd'


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

user_id=[]

@app.route("/")
def index():
	books = db.execute("SELECT * FROM books").fetchall()
	
	if 'user' in session:
		return render_template('index.html', books=books, username=escape(session ['user']))
	return render_template('login.html')
	

@app.route("/login", methods=['POST'])
def login():
	
	username = request.form.get('username')
	password = request.form.get('password')
	
	user = db.execute("SELECT * FROM users WHERE username = :username", {"username":username})
	
	if user.rowcount == 0:
		return render_template('error.html', message="Please Create an account.")
	
	elif db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username":username, "password":password}).rowcount > 1:
		return render_template('error.html', message="Username and password do not match.")
		
	elif db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username":username, "password":password}).rowcount == 1:
		session ['user'] = request.form['username']
		
		return redirect(url_for('index'))
	else:
		return render_template('error.html', message="looks like something went wrong, please try again")
		
		
@app.route("/signup", methods=['POST', 'GET'])
def signup():

	if request.method == "GET":
		return render_template('signup.html')
			
	elif request.method == "POST":
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
		username = request.form.get('username')
		password = request.form.get('password')
		
		# See if user name and password is already created
		if db.execute("SELECT * FROM users WHERE username = :username OR password = :password OR first_name = :first_name OR last_name = :last_name", {"username":username, "password":password, "first_name":first_name, "last_name":last_name}).rowcount > 0:
			return login()
		
		# create new user with the form data. Don't forget to hash password before final.
		else:
			db.execute("INSERT INTO users (first_name, last_name, username, password) VALUES (:first_name, :last_name, :username, :password)", {"first_name": first_name, "last_name": last_name, "username": username, "password": password})
			db.commit()
		return index()
		
@app.route("/logout")
def logout():
	# remove username from session.
	session.pop('user', None)
	return index()
	
	
@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search = request.form['search']
        search_escape = '%' + search + '%'
        
        
        # search by title, author, ISBN
        data = db.execute("SELECT * from books WHERE UPPER(title) LIKE UPPER(:search) OR UPPER(author) LIKE UPPER(:search) OR UPPER(isbn) LIKE UPPER (:search)", {"search": search_escape})
        db.commit()
        results = data.fetchall()
        
        # all in the search box will return all the tuples
        if len(results) == 0 and search == 'all':
            all_data=db.execute("SELECT * from books")
            results = all_data.fetchall()
        return render_template('books.html', books=results)
    return render_template('books.html')


@app.route("/review", methods=["POST"])
def review():
	"""Review a Book."""
	
	# Get form information
	review = request.form.get("review")
	stars = request.form.get("stars")
	username = session['user']
	user_id = db.execute("SELECT * FROM users WHERE username = :username", {"username":username}).keys()
	
	
	try:
		book_id = int(request.form.get("book_id"))
	except ValueError:
		return render_template("error.html", message="This is not a valid book")
		
	# Make sure book exists.
	if db.execute("SELECT * FROM books WHERE id = :id", {"id":book_id}).rowcount == 0:
		return render_template ("error.html", message="No such book with that id.")
	db.execute("INSERT INTO reviews (user_id, review, book_id, stars) VALUES (:user_id, :review, :book_id, :stars)", {"user_id": user_id, "review": review, "book_id": book_id, "stars": stars})
	db.commit()
	return render_template("success.html")
	
@app.errorhandler(404)
def page_not_found(error):
	return render_template('error.html', message="404 error, page not found")
