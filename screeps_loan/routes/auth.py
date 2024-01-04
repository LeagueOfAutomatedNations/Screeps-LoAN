from screeps_loan import app
from flask import Flask, session, redirect, url_for, escape, request, render_template
from screeps_loan.models.db import get_conn
import screepsapi.screepsapi as screepsapi
import screeps_loan.screeps_client as screeps_client
from screeps_loan.auth_user import AuthPlayer
import screeps_loan.services.session


@app.route("/auth/success")
def auth_request():
    return render_template("auth_sent.html")


@app.route("/auth/<token>")
def auth(token):
    query = "SELECT ign, id, screeps_id FROM users WHERE login_code=%s"
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(query, (token,))
    row = cursor.fetchone()
    if row is not None:
        session["username"] = row[0]
        session["my_id"] = row[1]
        session["screeps_id"] = row[2]
    return redirect(url_for("index"))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    # remove the username from the session if it's there
    session.pop("username", None)
    session.pop("my_id", None)
    return redirect(url_for("index"))


@app.route("/invite/accept/<token>")
def accept_alliance_invite(token):
    pass


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # TODO: Authenticate via url
        username = request.form["username"]
        api = screeps_client.get_client()
        auth = AuthPlayer(api)
        (id, token) = auth.auth_token(username)
        if id is not None:
            url = url_for("auth", token=token, _external=True)
            message = "Login to the League of Automated Nations %s" % url
            api.msg_send(id, message)
        return redirect(url_for("auth_request"))
    return render_template("login.html")
