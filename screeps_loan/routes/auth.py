from screeps_loan import app
from flask import Flask, session, redirect, url_for, escape, request, render_template
from screeps_loan.models.db import get_conn

@app.route('/auth/success')
def auth_request():
    return render_template('auth_sent.html')

@app.route('/auth/<token>')
def auth(token):
    query = "SELECT ign, id, screeps_id FROM users WHERE login_code=%s"
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(query, (token,))
    row = cursor.fetchone()
    if (row is not None):
        session['username'] = row[0]
        session['my_id'] = row[1]
        session['screeps_id'] = row[2]
    return redirect(url_for('index'))
