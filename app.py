from flask import Flask, request, render_template, redirect
from helpers import apology
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


connection = sqlite3.connect("database.db")
cursor = connection.cursor()

app = Flask(__name__)


session = []


@app.route("/")
def index():
    tasks = cursor.execute("SELECT * FROM tasks WHERE user_id = ?", session["id"])
    return render_template("index.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "GET":
        return render_template("register.html") 
    else:
        if not request.form.get("username"):
            return apology("must provide username")
        elif not request.form.get("password"):
            return apology("must provide password")
        elif not request.form.get("confirmation"):
            return apology("must re-enter password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")
        
        rows = cursor.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if (len.rows) != 0:
            return apology("the username already exists")
        
        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))
        cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        connection.commit()

        session["id"] = rows[0]["id"]
        return redirect("/")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    
    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    
    else:
        if not request.form.get("username"):
            return apology("must provide username")
        if not request.form.get("password"):
            return apology("must provide password")
        
        rows = cursor.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")
        
        session["id"] = rows[0]["id"]
        return redirect("/")
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
