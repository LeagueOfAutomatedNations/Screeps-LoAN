from screeps_loan import app
from flask import render_template, redirect, request, session, url_for, escape, flash
from werkzeug.utils import secure_filename
import os
import hashlib
import screeps_loan.models.alliances as alliances_model
import screeps_loan.models.invites as invites
import screeps_loan.models.users as users_model
from screeps_loan.routes.decorators import login_required
from screeps_loan.auth_user import AuthPlayer
import screeps_loan.services.users as users_service
import hashlib
import screeps_loan.screeps_client as screeps_client
import re

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    if re.match('^[\w|\s|-]+$', request.form['fullname']):
        fullname = request.form['fullname']

    if re.match('^\w+$', request.form['shortname']):
        shortname = request.form['shortname']

    if re.match('^[\w|-]+$', request.form['slack_channel']):
        slack_channel = request.form['slack_channel']
    else:
        slack_channel = None

    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)
    alliances_model.update_all_alliances_info(alliance['shortname'], shortname, fullname, slack_channel)
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

    if re.match(r'^\w+$', request.form['shortname']):
        shortname = request.form['shortname']
    else:
        shortname = re.sub(r'\w+', '', request.form['shortname'])

    alliances_model.create_an_alliance(my_id, fullname, shortname)
    return redirect(url_for("my_alliance"))


@app.route('/my/leave', methods=["POST"])
@login_required
def leave_alliance():
    users_model.update_alliance_by_screeps_id(session['screeps_id'], None)
    return redirect(url_for("my_alliance"))



@app.route('/invite', methods=["POST"])
@login_required
def invite_to_alliance():

    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)
    if (alliance is None):
        return "You are not in an alliance, can't invite anyone"

    username = request.form['username']

    # Make sure user is in database and game world.
    api = screeps_client.get_client()
    auth = AuthPlayer(api)
    ign = auth.id_from_name(username)

    if not ign:
        flash('User not present in game - remember usernames are case sensitive.')
        return redirect(url_for("my_alliance"))


    # Get database id
    id = users_model.user_id_from_db(username)

    if not id:
        flash('User not present in system - please try again later.')
        return redirect(url_for("my_alliance"))

    # Is user already in an alliance?
    current_alliance = users_model.alliance_of_user(id)
    if current_alliance:
        flash('User is already in an alliance.')
        return redirect(url_for("my_alliance"))


    invites.add_invite(id, alliance['shortname'], my_id)
    api.msg_send(ign, "You are invited to join %s \n\n%s" % (alliance['fullname'], url_for('list_invites', _external=True)))

    flash('Successfully invited user to your alliance')
    return redirect(url_for("my_alliance"))



@app.route('/kick', methods=["POST"])
@login_required
def kick_from_alliance():

    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)
    if (alliance is None):
        return "You are not in an alliance, can't kick anyone"

    username = request.form['username']

    # Make sure user is in database and game world.
    api = screeps_client.get_client()
    auth = AuthPlayer(api)
    ign = auth.id_from_name(username)

    if not ign:
        flash('User not present in game - remember usernames are case sensitive.')
        return redirect(url_for("my_alliance"))


    # Get database id
    user_id = users_model.user_id_from_db(username)

    if not user_id:
        flash('User not present in system - please try again later.')
        return redirect(url_for("my_alliance"))

    # Is user already in an alliance?
    current_alliance = users_model.alliance_of_user(user_id)
    if not current_alliance:
        flash('User is not in an alliance.')
        return redirect(url_for("my_alliance"))
    if current_alliance[1] != alliance[1]:
        flash('User is not in your alliance.')
        return redirect(url_for("my_alliance"))

    users_model.update_alliance_by_user_id(user_id, None)

    flash('Successfully kicked user from your alliance')
    return redirect(url_for("my_alliance"))
