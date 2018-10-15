import screepsapi.screepsapi as screepsapi
from flask import g

from screeps_loan import app


def get_client():
    conn = getattr(g, '_screeps_client', None)
    if conn is None:
        if 'API_TOKEN' in app.config:
            token = app.config['API_TOKEN']
            api = screepsapi.API(token=token)
        else:
            user = app.config['API_USERNAME']
            password = app.config['API_PASSWORD']
            api = screepsapi.API(user, password)

        g._screeps_client = api
    return g._screeps_client
