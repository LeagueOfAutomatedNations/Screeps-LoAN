import psycopg2
from flask import g
from screeps_loan import app

def get_conn():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = psycopg2.connect(database=app.config['DB'], user=app.config['DB_USERNAME'],
                         password=app.config['DB_PASSWORD'], host=app.config['DB_HOST'])
    return conn
