import psycopg2
from flask import g
from screeps_loan import app
import screepsapi.screepsapi as screepsapi
import os


def get_client():
    conn = getattr(g, "_screeps_client", None)
    if conn is None:
        if "API_TOKEN" in os.environ:
            token = os.environ["API_TOKEN"]
            api = screepsapi.API(token=token)
        else:
            user = os.environ["API_USERNAME"]
            password = os.environ["API_PASSWORD"]
            api = screepsapi.API(user, password)

        g._screeps_client = api
    return g._screeps_client
