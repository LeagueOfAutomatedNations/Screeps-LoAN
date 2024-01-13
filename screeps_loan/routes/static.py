from flask import render_template
from screeps_loan import app


@app.route("/tools")
def static_tools():
    return render_template("tools.html")


@app.route("/api")
def static_api():
    return render_template("api.html")
