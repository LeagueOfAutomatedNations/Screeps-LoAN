from flask import Flask, session, redirect, url_for, escape, request, render_template, flash, send_from_directory
from screeps_loan import app
app.config.from_envvar('SETTINGS')

import socket
import screeps_loan.cli.import_user
import screeps_loan.cli.maintenance

import screeps_loan.routes.auth
import screeps_loan.routes.alliances
import screeps_loan.routes.map
import screeps_loan.routes.my_alliance

@app.route('/obj/<filename>')
def get_obj(filename):
    return send_from_directory(app.config['OBJECT_STORAGE'], filename)

@app.route('/')
def index():
    return redirect(url_for('map'))

# set the secret key.  keep this really secret:
app.secret_key = app.config['SECRET_KEY']
