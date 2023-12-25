from flask import render_template, redirect, request, session, url_for, escape, flash
from screeps_loan import app


@app.route("/tools")
def static_tools():
    return render_template("tools.html")


@app.route("/api")
def static_api():
    return render_template("api.html")
