from flask import Flask, request, render_template, redirect
from helpers import apology
import sqlite3
from werkzeug import generate_password_hash


connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT NOT NULL, hash TEXT NOT NULL)")

cursor.execute("CREATE TABLE tasks(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, task_name TEXT NOT NULL, due_date TEXT, category TEXT, FOREIGN KEY (user_id) REFERENCES users (id))")

connection.commit()


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
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

        return redirect("/")
