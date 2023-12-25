from flask import (
    Flask,
    session,
    redirect,
    url_for,
    escape,
    request,
    render_template,
    flash,
    send_from_directory,
)
from screeps_loan import app
from flask_cors import cross_origin

app.config.from_envvar("SETTINGS")

import socket
import screeps_loan.cli.game_export
import screeps_loan.cli.import_rankings
import screeps_loan.cli.import_user
import screeps_loan.cli.maintenance
import screeps_loan.cli.manage

import screeps_loan.routes.auth
import screeps_loan.routes.alliances
import screeps_loan.routes.errors
import screeps_loan.routes.invites
import screeps_loan.routes.map
import screeps_loan.routes.my_alliance
import screeps_loan.routes.static
import screeps_loan.routes.userrankings

import screeps_loan.extensions.jinja


@app.route("/obj/<filename>")
@cross_origin(origins="*", send_wildcard=True, methods="GET")
def get_obj(filename):
    return send_from_directory(app.config["OBJECT_STORAGE"], filename)


@app.route("/")
def index():
    return redirect(url_for("alliance_rankings"))


@app.after_request
def add_header(response):
    if "Cache-Control" not in response.headers:
        response.headers[
            "Cache-Control"
        ] = "private, no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
    return response


# set the secret key.  keep this really secret:
app.secret_key = app.config["SECRET_KEY"]
