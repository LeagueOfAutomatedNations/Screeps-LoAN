import psycopg2
import psycopg2.extras
from flask import g
from screeps_loan import app
from psycopg2.extensions import STATUS_BEGIN, STATUS_READY
import os


def get_conn():
    conn = getattr(g, "_database", None)
    if conn is None:
        g._database = psycopg2.connect(
            database=os.environ["DB"],
            user=os.environ["DB_USERNAME"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
        )
    return g._database


def runQuery(query, params=None):
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if params is not None:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    conn.commit()
    return cursor


def find_one(query, params=None):
    return runQuery(query, params).fetchone()


def find_all(query, params=None):
    return runQuery(query, params).fetchall()


def execute(query, params=None):
    runQuery(query, params)
