import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import *
from sqlalchemy import *
from sqlbase import *

from helpers import apology, login_required, usd

# Configure application
template_dir = os.path.abspath('./templates') # ./templates  up the path into templates
app = Flask(__name__, template_folder=template_dir) # also set template folder path

app.config['FLASK_ENV']= "development"
app.config['FLASK_DEBUG']= True
app.config['FLASK_APP']="src/app.py"
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

engine = create_engine("sqlite:///database/ehub.db", echo=True)


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


# Make sure API key is set
#if not os.environ.get("API_KEY"):
 #   raise RuntimeError("API_KEY not set")

@app.route("/")
def index():
    return render_template("index.html")


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

        s = "SELECT name, hash, id FROM users WHERE name =(?)"
        res = db.execute(s, user)
        row= res.fetchone()
        
        if row != None:
            uhash= row[1]
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
        if len(password) <3:
            return apology("password too short")
        if password != confirmation:
            return apology("password and retyped passwords do not match!")


        # Check if user exists
        s = select([users.c.name]).where(users.c.name==user)
        res= db.execute(s)
        res = res.fetchone()
        if res and user == res[0]:
            return render_template("register.html", msg="Username in use")


        #generate pass hash
        passHash = generate_password_hash(password, "sha256")
        # Insert Query into DB
        ins = users.insert().values(name=user, hash=passHash)
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
        
        check = check_password_hash( usr, curPass)

        if not check:
            db.close()
            return render_template("changepass.html", msg="Current password wrong")
        else:
            query = "UPDATE users SET hash = ? WHERE users.id = ?"
            db.execute(query, passHash, session['user_id'])
            db.close()
            return render_template("changepass.html", msg="Password changed successfully")


    return render_template("changepass.html")

