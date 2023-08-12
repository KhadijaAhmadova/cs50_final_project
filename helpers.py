from flask import render_template


def apology(message):
    return render_template("apology.html", message=message)