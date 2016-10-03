from screeps_loan import app
from flask import render_template, redirect, request, session, url_for, escape
from werkzeug.utils import secure_filename
import os
import hashlib
import screeps_loan.models.alliances as alliances_model
import screeps_loan.models.users as users_model

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/my/uploadlogo', methods =['POST'])
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
def update_my_alliance_charter():
    charter = request.form['charter']
    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)

    alliances_model.update_charter_of_alliance(alliance['shortname'], charter)
    return (redirect(url_for('my_alliance')))

@app.route('/my')
def my_alliance():
    if ('username' not in session):
        return redirect(url_for('login'))
    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)
    return render_template('my.html', alliance = alliance)
