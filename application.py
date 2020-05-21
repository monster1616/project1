import os

from flask import Flask, session,render_template,request,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# for api
import requests


"""Application for flask...............""""
app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
   # raise RuntimeError("DATABASE_URL is not set")

 #if not os.getenv("postgres://iorynocojkwjgc:d6104889e6eeee320700f04b6012980b77506087bded1c13ed5e9d155c97a245@ec2-107-22-162-8.compute-1.amazonaws.com:5432/d22b8flhk40kgi"):
 #	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#app.config["DATABASE_URL"]="postgres://iorynocojkwjgc:d6104889e6eeee320700f04b6012980b77506087bded1c13ed5e9d155c97a245@ec2-107-22-162-8.compute-1.amazonaws.com:5432/d22b8flhk40kgi"
Session(app)

# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"))
# using Heroku url directly
engine = create_engine("postgres://iorynocojkwjgc:d6104889e6eeee320700f04b6012980b77506087bded1c13ed5e9d155c97a245@ec2-107-22-162-8.compute-1.amazonaws.com:5432/d22b8flhk40kgi")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/",methods=['GET','POST'])
def index():
	
	if request.method=='POST':
		user =request.form.get('username')
		pswrd=request.form.get('passwrd')

		#avoiding whitespaces problem
		if user!="" and pswrd!="":
			try:
				usr=db.execute("SELECT * FROM users WHERE username=:user AND pswrd=:pswrd",{'user':user,'pswrd':pswrd}).fetchone()
				
				if usr.username== user:
					session["user"]=usr.username
					session['user_id']=usr.id
					return render_template('search.html')
				else: 
					return render_template("index.html",message="Invalid username or password")
			except Exception as e:

				return render_template("index.html",message='Invalid username or password')
		else:
			return render_template("index.html",message='Invalid username or password')
	else:
		return render_template('index.html')

    
@app.route("/register",methods=['GET','POST'])
def register():
	if request.method=='GET':
		return render_template('register.html')
	else:
		username=request.form.get('username')
		pswrd=request.form.get('passwrd')
		
		

		try:
			if username.strip()!="" and pswrd.strip()!="":
				db.execute("INSERT INTO users (username,pswrd) VALUES(:username,:pswrd)",{'username':username,'pswrd':pswrd})
				db.commit()
				return "Account has been created"
			else:
				return render_template("register.html",message="invalid input")
		except Exception as e:
			return render_template("register.html",message="User name already exists")
		
@app.route("/search",methods=['GET','POST'])
def search():
	name=request.form.get('srch')
	keyword=request.form.get('keyword')
	if name=='isbn':
		# searching by isbn and also using LIKE in SQL
		lists=db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",{'isbn':'%'+keyword+'%'}).fetchall()
	elif name=='title':
		# searching by title name and also using LIKE in SQL
		lists=db.execute("SELECT * FROM books WHERE title LIKE :title",{'title':'%'+keyword+'%'}).fetchall()
	elif name=='author':
		# searching by author name and also using LIKE in SQL
		lists=db.execute("SELECT * FROM books WHERE author LIKE :author",{'author':'%'+keyword+'%'}).fetchall()

	if request.method=='GET':
		return render_template('search.html')
	else:
		
		return render_template('search.html',lists=lists)

@app.route('/book_details/<int:book_id>',methods=['GET','POST'])
def book_details(book_id):
	message=""  # message after submitting the review
	details=db.execute("SELECT * FROM books WHERE id=:book_id",{'book_id':book_id}).fetchone()
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "BKMKb4vaIpvUbGUseF2Yg", "isbns":details.isbn })
	data=res.json()
	avg_ratings=data["books"][0]['average_rating']
	num_ratings=data["books"][0]['work_ratings_count']
	#return jsonify(data["books"][0]['average_rating'])
	if request.method=='POST':
		user_id=session["user_id"]
		isbn=details.isbn
		ratings=int(request.form.get("rating"))
		comment=request.form.get("comment")
		try:
			db.execute("INSERT INTO reviews(rating,comment,isbn,user_id)VALUES(:rating,:comment,:isbn,:user_id)",{'rating':ratings,'comment':comment.strip(),'isbn':isbn,'user_id':user_id})
			db.commit()
			message="reviews have been submitted"
		except Exception as e:
			message=str(e) # in case of eny error


	all_reviews=db.execute("SELECT reviews.rating,reviews.comment,users.username FROM reviews INNER JOIN users ON reviews.user_id=users.id WHERE reviews.isbn=:isbn",{'isbn':details.isbn}).fetchall()
	return render_template('book_details.html',avg_ratings=avg_ratings,num_ratings=num_ratings,details=details,message=message,all_reviews=all_reviews)






