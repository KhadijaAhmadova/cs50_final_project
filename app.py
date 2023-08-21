from flask import Flask, request, render_template, redirect, session
from helpers import apology, login_required
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)


app.secret_key = "session_secret_key"


@app.route("/")
@login_required
def index():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = (?)", (session.get("user_id"),))
    tasks = cursor.fetchall()
    return render_template("index.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    if request.method == "GET":
        return render_template("register.html") 
    elif request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")
        elif not request.form.get("password"):
            return apology("must provide password")
        elif not request.form.get("confirmation"):
            return apology("must re-enter password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")
        
        cursor.execute("SELECT * FROM users WHERE username = (?)", (request.form.get("username"),))
        rows = cursor.fetchall()

        if len(rows) != 0:
            return apology("the username already exists")
        
        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))
        cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        connection.commit()

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    
    session.clear()

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    if request.method == "GET":
        return render_template("login.html")
    
    elif request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")
        if not request.form.get("password"):
            return apology("must provide password")
        
        cursor.execute("SELECT * FROM users WHERE username = (?)", (request.form.get("username"),))
        rows = cursor.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")
        
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")
