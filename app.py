from flask import Flask, request, render_template, redirect, session, url_for
from flask_session import Session
from helpers import apology, login_required
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, task, due, completion_status, priority, details FROM tasks WHERE user_id = (?)", (session.get("user_id"),)) # cursor object
    task_data = cursor.fetchall() # list of touples
    tasks = [] # list of dictionaries

    for task in task_data:
        task_dict = {
            "id" : task[0],
            "task": task[1],
            "due": task[2],
            "completion_status": task[3],
            "priority": task[4],
            "details": task[5]
        }
        tasks.append(task_dict) # appending dict for each task to the list of dictionaries

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
        cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))

        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        session["user_id"] = cursor.fetchone()[0]

        connection.commit()
        cursor.close()
        connection.close()

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

        cursor.close()
        connection.close()

        return redirect("/")
    

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():

    if request.method == "GET":
        return render_template('add_task.html')
    
    elif request.method == "POST":

        task = request.form.get('task')
        due = request.form.get('due')
        completion_status = request.form.get('completion_status')
        priority = request.form.get('priority')
        details = request.form.get('details')

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("INSERT INTO tasks (user_id, task, due, completion_status, priority, details) VALUES (?, ?, ?, ?, ?, ?)", (session.get("user_id"), task, due, completion_status, priority, details))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect("/")
    

@app.route("/update_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def update_task(task_id):

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    if request.method == "GET":

        cursor.execute("SELECT id, task, due, completion_status, priority, details FROM tasks WHERE user_id = (?) AND id = (?)", (session.get("user_id"), task_id))
        task_tuple = cursor.fetchone() # a tuple

        task = {
            "id" : task_tuple[0],
            "task": task_tuple[1],
            "due": task_tuple[2],
            "completion_status": task_tuple[3],
            "priority": task_tuple[4],
            "details": task_tuple[5]
        }

        return render_template("update_task.html", task=task)
    
    elif request.method == "POST":

        task = request.form.get('task')
        due = request.form.get('due')
        completion_status = request.form.get('completion_status')
        priority = request.form.get('priority')
        details = request.form.get('details')
        
        cursor.execute("UPDATE tasks SET task=?, due=?, completion_status=?, priority=?, details=? WHERE id=?", (task, due, completion_status, priority, details, task_id))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect("/")
    

@app.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM tasks WHERE user_id = ? AND id = ?", (session.get("user_id"), task_id))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")
