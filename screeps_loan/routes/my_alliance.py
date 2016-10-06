from screeps_loan import app
from flask import render_template, redirect, request, session, url_for, escape, flash
from werkzeug.utils import secure_filename
import os
import hashlib
import screeps_loan.models.alliances as alliances_model
import screeps_loan.models.users as users_model
from screeps_loan.routes.decorators import login_required
from screeps_loan.auth_user import AuthPlayer
import screeps_loan.models.users as users_model
import screeps_loan.services.users as users_service
import hashlib
import screeps_loan.screeps_client as screeps_client


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/my/uploadlogo', methods =['POST'])
@login_required
def upload_my_alliance_logo():
    # check if the post request has the file part
    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)

    if (alliance is None):
        return "You are not in an alliance, can't do this"


    if 'logo' not in request.files:
        #flash('No file part')
        return redirect(url_for('my'))
    file = request.files['logo']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
    #    flash('No selected file')
        return redirect(url_for('my'))
    if file and allowed_file(file.filename):
        filename = secure_filename(hashlib.sha512(os.urandom(128)).hexdigest()[0: 15])
        ext = file.filename.rsplit('.', 1)[1]
        filename = filename + '.' + ext
        file.save(os.path.join(app.config['OBJECT_STORAGE'], filename))
        alliances_model.update_logo_of_alliance(alliance['shortname'], filename)
        return redirect(url_for('my_alliance'))


@app.route('/my/updatecharter', methods=["POST"])
@login_required
def update_my_alliance_charter():
    charter = request.form['charter']
    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)

    alliances_model.update_charter_of_alliance(alliance['shortname'], charter)
    return (redirect(url_for('my_alliance')))


@app.route('/my/updateprofile', methods=["POST"])
def update_my_alliance_profile():
    fullname = request.form['fullname']
    shortname = request.form['shortname']
    slack_channel = request.form['slack_channel']
    color = request.form['color']
    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)
    alliances_model.update_all_alliances_info(alliance['shortname'], shortname, fullname, slack_channel, color)
    return (redirect(url_for('my_alliance')))

@app.route('/my')
@login_required
def my_alliance():
    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)
    if (alliance is None):
        return render_template("alliance_creation.html")
    return render_template('my.html', alliance = alliance)


@app.route('/my/create', methods=["POST"])
@login_required
def create_an_alliance():
    my_id = session['my_id']
    fullname = request.form['fullname']
    shortname = request.form['shortname']
    color = request.form['color']
    alliances_model.create_an_alliance(my_id, fullname, shortname, color)
    return redirect(url_for("my_alliance"))


@app.route('/invite', methods=["POST"])
@login_required
def invite_to_alliance():

    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)
    if (alliance is None):
        return "You are not in an alliance, can't invite anyone"

    username = request.form['username']
    api = screeps_client.get_client()

    auth = AuthPlayer(api)
    id = auth.id_from_name(username)
    users_model.update_alliance_by_screeps_id(id, alliance['shortname'])
    #(id, token) = auth.auth_token(username)

    #if (id is not None):
    #    api.msg_send(id, "You are invited to join %s, click for more info: \n\n" % alliance+
    #                 url_for('accept_alliance_invite', token=token, _external=True))
    flash('Successfully add user to your alliance')
    return redirect(request.referrer)
