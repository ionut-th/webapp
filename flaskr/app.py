import os, time

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session

from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import *
from sqlalchemy import *
from sqlbase import *
from helpers import *
from werkzeug.utils import secure_filename



# Configure application
UPLOAD_FOLDER = '/flaskr/upload'
ALLOWED_EXTENSION = {'jpg', 'png', 'jpeg'}


# ./templates  up the path into templates
template_dir = os.path.abspath('./flaskr/templates')
# also set template folder path
app = Flask(__name__, template_folder=template_dir)
app.config.from_object("config.DevelopmentConfig")
# configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
engine = create_engine("sqlite:///flaskr/database/ehub.db", echo=True)

app.config["FLASK_ENV"] = "production"
app.config["FLASK_APP"] = "flaskr/app.py"
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

categories = [
    'General'
    'Job Listing',
    'Sell General',
    'Sell Electronics',
    'Sell AUTO',
    'Sell Houses/ Real Estate'
    'Lost / Found'
]



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

@app.route("/search", methods=['GET', 'POST'])
def search():
    # TODO
    # Search all posts by selected cateogry and return a list of posts ordered by latest post
    if request.method == "POST":
        db= engine.connect()
        cat = request.form.get("search_category")
        inputSearch = request.form.get("search")

        s = "SELECT * FROM posts WHERE posts.title LIKE "

        # If we get more than one search word
        # construct a query from number of words
        if cat.lower() == "general":
            section=""
        else:
            section= " AND posts.section == " + cat

        fields = inputSearch.split()
        _query = ""
        param=""
        if len(fields) > 1:
            for f in fields:
                _temp = "'%"+ f + "%'"
                _query += " or posts.title LIKE " + _temp

            param = "'%"+fields[0] +"%'" + _query + section 
            res = db.execute(s+param)
        else:
            param = "'%"+ fields[0] + "%'" + section
            res = db.execute(s+param)

        #print(s+param + section, flush=True)

        return render_template("search.html",  msg="Search Results ", searchResult=res )
   

@app.route("/")
def index():

    # TODO
    # When reached this route select from the database 10 most recent posts
    # Create a list with titles and descriptions
    # When clicked on links, the link should redirect/render the post page
    s = "SELECT * FROM posts ORDER BY posts.postDate DESC LIMIT 20"
    db = engine.connect()
    res = db.execute(s)
    return render_template("index.html", listPosts=res)


@app.route("/myposts", methods=["GET", "POST"])
@login_required
def myposts():
    # TODO
    # When user routes to myposts preset a list of posts from the database with his ID
    # Also preset a button for each post to allow deletion of the post
    db = engine.connect()
    userID = session['user_id']
    s = "SELECT * FROM posts WHERE posts.owner_id == (?) ORDER BY posts.postDate DESC"

    if request.method == "POST":
        post_id = request.form.get("delete_button")
        upd = "DELETE FROM posts WHERE posts.id == (?) AND posts.owner_id==(?)"
        db.execute(upd, post_id, userID)
        res = db.execute(s, userID)

        if res != None:
            return render_template("myposts.html", msg="Post deleted Successfully!", listPosts=res, listSections=categories)
        else:
            return redirect("/myposts")

    res = db.execute(s, userID)
    if res != None:
        return render_template("myposts.html",
                               listPosts=res,
                               listSections=categories
                               )

    return render_template("myposts.html")


@app.route("/newpost", methods=["GET", "POST"])
@login_required
def newpost():
    # TODO
    # Render a page where you can create a new post
    # Query the database to add the new post
    if request.method == "POST":

        _title = request.form.get("title")
        descr = request.form.get("description")
        catg = request.form.get("category")
        phone = request.form.get("phone")
        city = request.form.get("city")
        date = datetime.now().replace(microsecond=0)

        if not _title or len(_title) < 6:
            return render_template("newpost.html", error="Please provide all the details")
        if not descr or len(descr) < 6:
            return render_template("newpost.html", error="Please provide all the details")
        if not catg or catg == "Category":
            return render_template("newpost.html", error="Please provide all the details")
        if not phone or len(phone) < 6:
            return render_template("newpost.html", error="Please provide all the details")
        if not city or len(city) < 2:
            return render_template("newpost.html", error="Please provide all the details")

        print(_title, descr, catg, phone, city, date, flush=True)

        db = engine.connect()
        userId = session['user_id']
        ins = posts.insert().values(
            owner_id=userId,
            title=_title,
            details=descr,
            city=city,
            phone=phone,
            section=catg,
            postDate=date
        )
        print(ins, flush=True)
        db.execute(ins)

        db.close()
        return render_template("newpost.html", msg="Post Created Successfully")
    return render_template("newpost.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        db = engine.connect()

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        user = request.form.get("username").lower()
        pwd = request.form.get("password")

        # Ensure username exists and password is correct

        s = "SELECT username, hash, id FROM users WHERE username =(?)"
        res = db.execute(s, user)
        row = res.fetchone()

        if row != None:
            uhash = row[1]
            _id = row[2]
        else:
            return render_template("login.html", msg="User does not exist")

        if not check_password_hash(uhash, pwd):
            return render_template("login.html", msg="User or password error")

        # Remember which user has logged in
        session["user_id"] = _id
        db.close()
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()
    db = engine.connect()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # get input data
        user = request.form.get("username").lower()
        password = request.form.get("password").lower()
        confirmation = request.form.get("confirmation").lower()
        # check for valid input
        if len(user) < 3:
            return apology("user too short", 403)
        if len(password) < 3:
            return apology("password too short")
        if password != confirmation:
            return apology("password and retyped passwords do not match!")

        # Check if user exists
        s = select([users.c.username]).where(users.c.username == user)
        res = db.execute(s)
        res = res.fetchone()
        if res and user == res[0]:
            return render_template("register.html", msg="Username in use")

        # generate pass hash
        passHash = generate_password_hash(password, "sha256")
        # Insert Query into DB
        ins = users.insert().values(username=user, hash=passHash)
        db.execute(ins)

        # Redirect user to home page
        db.close()
        return redirect("/login")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        db.close()
        return render_template("register.html")


def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():

    if request.method == "POST":
        db = engine.connect()

        if not request.form.get("currentPass"):
            return render_template("changepass.html", msg="Current password wrong")
        if not request.form.get("newPass"):
            return render_template("changepass.html", msg="You did not enter a new password")
        if not request.form.get("confirmation"):
            return render_template("changepass.html", msg="Please retype your new password again correctly")

        curPass = request.form.get("currentPass")
        newPass = request.form.get("newPass")
        confirm = request.form.get("confirmation")

        if newPass != confirm:
            return render_template("changepass.html", msg="New password does not match, please retype your password confirmation")

        passHash = generate_password_hash(newPass, "sha256")

        s = "SELECT hash FROM users WHERE id = (?)"
        res = db.execute(s, session['user_id'])
        res = res.fetchone()
        if res != None:
            usr = res[0]
        else:
            db.close()
            return redirect("/login")

        check = check_password_hash(usr, curPass)

        if not check:
            db.close()
            return render_template("changepass.html", msg="Current password wrong")
        else:
            query = "UPDATE users SET hash = ? WHERE users.id = ?"
            db.execute(query, passHash, session['user_id'])
            db.close()
            return render_template("changepass.html", msg="Password changed successfully")

    return render_template("changepass.html")
