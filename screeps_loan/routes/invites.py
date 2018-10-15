import json

from flask import render_template, redirect, session, url_for, abort

import screeps_loan.models.db as db
import screeps_loan.models.invites as invites
import screeps_loan.models.users as users_model
from screeps_loan import app
from screeps_loan.routes.decorators import login_required


@app.route('/my/invites')
@login_required
def list_invites():
    # Is user already in an alliance?
    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)
    if alliance:
        return redirect(url_for("my_alliance"))

    my_invites = invites.get_invites_by_user(session['my_id'])
    return render_template("my_invites.html", invites=my_invites)


@app.route('/my/invites/<inviteid>/delete.js', methods=['POST'])
@login_required
def invite_decline(inviteid):
    my_id = session['my_id']
    invite = invites.get_invite_by_id(inviteid)
    if not invite:
        abort(404)

    if invite['user_id'] != my_id:
        abort(404)

    invites.del_invite_by_id(inviteid)
    db.get_conn().commit()
    return json.dumps(True)


@app.route('/my/invites/<inviteid>/accept.js', methods=['POST'])
@login_required
def invite_accept(inviteid):
    my_id = session['my_id']

    invite = invites.get_invite_by_id(inviteid)
    if not invite:
        abort(404)
    if invite['user_id'] != my_id:
        abort(404)

    # Add user to appropriate alliance.
    users_model.update_alliance_by_user_id(my_id, invite['alliance'])

    # Remove all pending invites from user.
    invites.del_invites_by_user(my_id)

    db.get_conn().commit()

    # Return true
    return json.dumps(True)
