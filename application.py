#export FLASK_APP=application.py
#export FLASK_DEBUG=1
#export DATABASE_URL=postgres://toynqapecjnonn:33475b234e05ed42573fc3c9bb42b3d8befa469fec84c9bdf4f0fe773649430d@ec2-54-243-216-33.compute-1.amazonaws.com:5432/ddlv82quhm4u3l
import os
import psycopg2
from goodreads import *
DATABASE_URL = os.environ['DATABASE_URL']
import sys
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


from flask import Flask, session, render_template, request, url_for, redirect
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

# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"))
#db = scoped_session(sessionmaker(bind=engine))
db = conn.cursor()


@app.route("/")
def index(message=None):
	if session.get("login") is None:
		session["login"]=False
	if session.get("login") == True:
		return redirect("/search")
	return render_template("index.html",message=message)

@app.route("/signup",methods=['GET','POST'])
def signup():
	message = None
	if request.method == "POST":
		u_id = request.form.get("inputID")
		password = request.form.get("inputPassword")
		db.execute("SELECT user_id,password FROM accounts WHERE user_id = %s",(u_id,))
		if db.fetchall() != []:
			message="Username has already taken!"
		else:
			db.execute("INSERT INTO accounts (user_id,password) VALUES (%s,%s)",(u_id,password))
			conn.commit()
			session["login"] = True
			session["user_id"] = u_id
			return redirect('/search')
	return render_template("signup.html",message=message)
@app.route('/login',methods=['GET','POST'])
def login():
	if session.get("login") == False:
		message = None
		if request.method == "POST":
			u_id = request.form.get("inputID")
			password = request.form.get("inputPassword")
			db.execute("SELECT * FROM accounts WHERE user_id = %s and password =%s",(u_id,password))
			if db.fetchall() == []:
				message="Wrong Password or ID"
			else:
				session["login"] = True
				session["user_id"] = u_id
				return redirect('/search')
		return render_template("login.html",message=message)
	return redirect('/search')
	
@app.route('/search',methods=['GET','POST'])
def search():
	message = None
	res = None
	if request.method == "POST":
		isbn = request.form.get("isbn",None)
		author = request.form.get("author",None)
		title = request.form.get("title",None)
		if isbn:
			res = make_request(param=isbn)
		elif author:
			res = make_request(param=author)
		elif title:
			res = make_request(param=title)
		else:
			message="Please fill one of the forms."
		print(res[0], file=sys.stdout)
	return render_template("search.html",message=message,res=res)

@app.route('/book/<code>',methods=['GET','POST'])
def book(code):
	reviews = None
	check = True
	session['book_id'] = code
	if request.method == 'POST' and can_review():
		message = request.form.get("message")
		db.execute("INSERT INTO reviews (book_id,review,acc_id) VALUES (%s,%s,(SELECT id FROM accounts WHERE user_id=%s))",(session['book_id'],message,session["user_id"]))
		conn.commit()
		
	if request.method == 'GET' or check:
		db.execute("SELECT review,acc_id FROM reviews WHERE book_id=%s",(session['book_id'],))
		reviews = db.fetchall()
		duzen = {}
		print(session.get("book_id"), file=sys.stdout)
		for rev in reviews:
			acc_id = rev[1]
			db.execute("SELECT user_id FROM accounts WHERE id=%s",(acc_id,))
			user_name = db.fetchall()
			duzen[user_name[0][0]] = rev[0]
		reviews = duzen
		print(reviews, file=sys.stdout)
		#reviews = reviews
	res = get_reviews(code) # good read api book author and staff
	return render_template("book.html",res=res,reviews=reviews)

def can_review():
	u_id = session.get('user_id')
	book_id = session.get("book_id")
	if u_id is not None:
		db.execute("SELECT acc_id FROM reviews WHERE acc_id IN (SELECT id FROM accounts WHERE user_id =%s) and book_id=%s",(u_id,book_id))
		if db.fetchall() == []:
			return True
		return False
	return False
@app.route('/logout')
def logout():
	session["login"] = False
	return render_template("logout.html")
