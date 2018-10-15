from flask import redirect, url_for, send_from_directory
from flask_cors import cross_origin

from screeps_loan import app

app.config.from_envvar('SETTINGS')


@app.route('/obj/<filename>')
@cross_origin(origins="*", send_wildcard=True, methods="GET")
def get_obj(filename):
    return send_from_directory(app.config['OBJECT_STORAGE'], filename)


@app.route('/')
def index():
    return redirect(url_for('alliance_rankings'))


@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'private, no-store, no-cache, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
    return response


# set the secret key.  keep this really secret:
app.secret_key = app.config['SECRET_KEY']
