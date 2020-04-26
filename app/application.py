import os
import psycopg2

from flask import Flask, session, render_template, request, redirect, abort, flash
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

signed_in = []

@app.route("/")
def index():
	if not session.get('signed_in'):
		return render_template('login.html')
	else:
		return render_template('index.html')

@app.route("/login", methods=['POST'])
def admin_login():

	if request.method == 'POST':
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
			session['signed_in'] = True
		else:
			return render_template('error.html', message="invalid login attempt")
	return index()
