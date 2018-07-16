import os
import requests

from flask import Flask, render_template, session, request
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
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

USER_ID = [0]

def get_user_id():
    return USER_ID[0]

def set_user_id(user_id):
    USER_ID[0] = user_id
    return USER_ID[0]

@app.route("/")
def index():
    """ Frontpage. Search prompt. """
    # get userid
    user_id = get_user_id()  
    if user_id == 0:
        return render_template("login.html")

    # get all collections of userid
    # collections = db.execute("SELECT * FROM user_collections WHERE user_id = 1").fetchall()

    # get all books in all collections of userid
    # query = "SELECT books.id AS mybook_id, collections.id AS mycollection_id, collections.collection_name, books.title, books.author, books.isbn "
    # query = query + "FROM user_book_collections UBC, user_collections UC, collections, books "
    # query = query + "WHERE UBC.user_id = UC.user_id "
    # query = query + "AND UBC.user_id = :user_id "
    # query = query + "AND UBC.collection_id = UC.collection_id "
    # query = query + "AND UBC.collection_id = collections.id "
    # query = query + "AND UBC.book_id = books.id "
    # mybooks = db.execute(query, {"user_id": user_id}).fetchall()
    # return render_template("index.html", mybooks=mybooks)        
    return render_template("index.html", mybooks={})        


@app.route("/register")
def register():
    return render_template("register.html")    

@app.route("/do_register", methods=["POST"])
def do_register():
    user_id = request.form.get("user_id")
    password = request.form.get("password")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    if user_id in (None, ''):
        return render_template("register.html", message="Please enter your email address.", alert_class="alert-warning", user_id=user_id, first_name=first_name, last_name=last_name)
    if password in (None, ''):
        return render_template("register.html", message="Please enter your password.", alert_class="alert-warning", user_id=user_id, first_name=first_name, last_name=last_name)
    if first_name in (None, ''):
        return render_template("register.html", message="Please enter your first name.", alert_class="alert-warning", user_id=user_id, first_name=first_name, last_name=last_name)
    if last_name in (None, ''):
        return render_template("register.html", message="Please enter your last name.", alert_class="alert-warning", user_id=user_id, first_name=first_name, last_name=last_name)        

    query = "SELECT * FROM users "
    query = query + "WHERE email_address = :user_id "
    user = db.execute(query, {"user_id": user_id}).fetchone()
    if user is None:
        query = "INSERT INTO users (email_address, password, first_name, last_name) "
        query = query + "VALUES (:user_id, :password, :first_name, :last_name)"
        db.execute(query, {"user_id": user_id, "password": password, "first_name": first_name, "last_name": last_name})
        db.commit()
        return render_template("login.html", message="User is successfully registered.", alert_info="alert-success")
    else:
        return render_template("register.html", message="User ID is already registered!", alert_class="alert-warning", user_id=user_id, first_name=first_name, last_name=last_name)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/do_login", methods=["POST"])
def do_login():
    user_id = request.form.get("user_id")
    password = request.form.get("password")

    if user_id in (None, ''):
        return render_template("login.html", message="Please enter your user id.", alert_class="alert-warning", user_id=user_id)

    query = "SELECT * FROM users "
    query = query + "WHERE email_address = :user_id "
    user = db.execute(query, {"user_id": user_id}).fetchone()
    if user is None:
        return render_template("login.html",message="Incorrect user ID or password.", alert_class="alert-warning", user_id=user_id)

    if password == user.password:
        # USER_ID = user.id        
        set_user_id(user.id)
        # get all books in all collections of userid
        query = "SELECT books.id AS mybook_id, collections.id AS mycollection_id, collections.collection_name, books.title, books.author, books.isbn "
        query = query + "FROM user_book_collections UBC, user_collections UC, collections, books "
        query = query + "WHERE UBC.user_id = UC.user_id "
        query = query + "AND UBC.user_id = :user_id "
        query = query + "AND UBC.collection_id = UC.collection_id "
        query = query + "AND UBC.collection_id = collections.id "
        query = query + "AND UBC.book_id = books.id "
        mybooks = db.execute(query, {"user_id": user.id}).fetchall()
        
        return render_template("index.html", mybooks={}, alert_info="alert-success", message="")
        #return render_template("index.html", mybooks=mybooks, alert_info="alert-success", message="")
    else:
        return render_template("login.html",message="Incorrect user ID or password.", alert_class="alert-warning", user_id=user_id)

@app.route("/logout")
def logout():
    set_user_id(0)
    return render_template("login.html")

@app.route("/search/", methods=["POST"])
def search():
    user_id = get_user_id()  
    if user_id == 0:
        return render_template("login.html")    

    search_string = request.form.get("search_string")

    if search_string == '':
        return render_template("index.html", mybooks={})

    search_string = search_string.upper()
    search_string = "%" + search_string + "%"
    
    query = "SELECT id as mybook_id, title, author, isbn FROM books "
    query = query + "WHERE upper(title) LIKE :search_string OR "
    query = query + " upper(author) LIKE :search_string OR"
    query = query + " upper(isbn) LIKE :search_string"
    books = db.execute(query, {"search_string": search_string}).fetchall()

    #if books is None:        
    if len(books) == 0:
        #return "No books found"
        return render_template("index.html",mybooks={}, alert_class="alert-warning", message="No books found.")

    return render_template("index.html", mybooks=books, alert_class="alert-warning", message="")

@app.route("/book/<int:book_id>")
def book(book_id):
    # get userid
    user_id = get_user_id()  
    if user_id == 0:
        return render_template("login.html")

    """Lists details about a book."""
    query = "SELECT * FROM books WHERE id = :book_id"
    if db.execute(query, {"book_id": book_id}).rowcount == 0:
        return render_template("error.html", message="Book not found: " + str(book_id))

    query = "SELECT books.id, title, author, isbn, users.id as review_user_id, first_name, last_name, review, rating "
    query = query + "FROM books LEFT OUTER JOIN reviews "
    query = query + "ON reviews.book_id = books.id "
    query = query + "LEFT OUTER JOIN users "
    query = query + "ON reviews.user_id = users.id "
    query = query + "WHERE books.id = :book_id"

    # query = "SELECT books.id, title, author, first_name, last_name, review, rating "
    # query = query + "FROM books, reviews "
    # query = query + "WHERE books.id = :book_id "
    # query = query + "AND reviews.book_id *= :book_id "
    # query = query + "AND reviews.user_id = users.id"
    book_reviews = db.execute(query, {"book_id": book_id}).fetchall()    

    isbn = book_reviews[0].isbn
    isbn = isbn.strip()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "TfuwMgDmde8R6r1DOW2M3w", "isbns": isbn})
    if res:
        jason_data = res.json()        
        review_count = jason_data["books"][0]["work_reviews_count"]
        average_score = jason_data["books"][0]["average_rating"]
    else:
        review_count = 0
        average_score = 0

    return render_template("book.html", book=book_reviews, isbn=isbn, user_id=user_id, review_count=review_count, average_score=average_score)


@app.route("/save_review", methods=["POST"])
def save_review():
    """Save a review."""
    # get userid
    user_id=get_user_id()
    if user_id == 0:
        render_template("login.html")

    # Get form information.
    book_id = int(request.form.get("book_id"))
    review = request.form.get("review")
    try:
        # rating = int(request.form.get("rating"))
        rating = request.form.get("rating")
        if (rating):
            rating = int(rating)
    except ValueError:
        return render_template("error.html", message="Invalid rating.")    
    
    if review and rating:
        query = "INSERT INTO reviews "
        query = query + "(user_id, book_id, review, rating) "
        query = query + "VALUES (:user_id, :book_id, :review, :rating) "
        db.execute(query, {"user_id": user_id, "book_id": book_id, "review": review, "rating": rating})
        db.commit()                  
        message="Review is successfully saved."
        alert_class="alert-success"
    else:
        message="Please enter a review and rating."
        alert_class="alert-warning"

    query = "SELECT books.id, title, author, isbn, users.id as review_user_id, first_name, last_name, review, rating "
    query = query + "FROM books LEFT OUTER JOIN reviews "
    query = query + "ON reviews.book_id = books.id "
    query = query + "LEFT OUTER JOIN users "
    query = query + "ON reviews.user_id = users.id "
    query = query + "WHERE books.id = :book_id"
    book_reviews = db.execute(query, {"book_id": book_id}).fetchall()    

    isbn = book_reviews[0].isbn
    isbn = isbn.strip()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "TfuwMgDmde8R6r1DOW2M3w", "isbns": isbn})
    if res:
        jason_data = res.json()        
        review_count = jason_data["books"][0]["work_reviews_count"]
        average_score = jason_data["books"][0]["average_rating"]
    else:
        review_count = 0
        average_score = 0                

    return render_template("book.html", book=book_reviews, isbn=isbn, user_id=user_id, review_count=review_count, average_score=average_score, message=message, alert_class=alert_class)

@app.route("/api/<string:isbn>")
def api(isbn):

    user_id = get_user_id()  
    if user_id == 0:
        return render_template("login.html")

    isbn = isbn.strip()
    query = "SELECT * FROM books "
    query = query + "WHERE isbn = :isbn"
    book = db.execute(query, {"isbn": isbn}).fetchone()
    if len(book) == 0:
        return render_template("error.html", message="Book with ISBN number " + isbn + " not found in the database.")

    #jason_data = "{\n"
    #jason_data = jason_data + '"title:" "' + book.title +  '",\n'
    #jason_data = jason_data + "}\n"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "TfuwMgDmde8R6r1DOW2M3w", "isbns": isbn})
    jason_data = res.json()    
    # r = rc["books"][0]["id"]
    #book = res['books'][0]
    #title = 
    #author = 
    #year =
    #isbn = 
    review_count = jason_data["books"][0]["work_reviews_count"]
    average_score = jason_data["books"][0]["average_rating"]
    #review_count = book['work_reviews_count']
    #average_score = book['average_rating']
    #return render_template("error.html", message=r) # res.text
    return render_template("jason_data.html", title=book.title, author=book.author, year=book.year,isbn=book.isbn, review_count=review_count, average_score=average_score)
    #return "TO DO"

    