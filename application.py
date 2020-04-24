import os
import psycopg2

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database comment
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
	#flights = db.execute("SELECT * FROM books LIMIT 5").fetchall()
	return render_template("index.html")

if __name__ == "__main__":
	port = int(os.enviorn.get("PORT", 8080))
	app.run(host="0.0.0.0", port=port)
