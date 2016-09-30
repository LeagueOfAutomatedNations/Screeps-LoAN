from db import get_conn
import hashlib
import os
import datetime


class AuthPlayer(object):
    def __init__(self, api_client):
        self.api_client = api_client

    def random_token(self):
        return hashlib.sha512(os.urandom(128)).hexdigest()[0: 15]


    def player_id_from_db(self, name):
        query = "SELECT screeps_id FROM users WHERE ign=%s"
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(query, (name,))
        row = cursor.fetchone()
        if (row is not None):
            return row[0]
        return None

    def player_id_from_api(self, name):
        resp = self.api_client.user_find(name)
        if ((resp['ok'] == 1) and (resp['user'] is not None)):
            return resp['user']['_id']
        return None

    def store_id(self, name, id):
        query = "INSERT INTO users(ign, screeps_id) VALUES(%s, %s)"
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(query, (name, id))
        conn.commit()

    def id_from_name(self, name):
        id = self.player_id_from_db(name)
        if (id is None):
            id = self.player_id_from_api(name)
            self.store_id(name, id)
        return id


    def auth_token(self, name):
        id = self.id_from_name(name)
        token = None
        if id is not None:
            token = self.random_token()
            query = "UPDATE users SET login_code=%s, login_code_created_at=%s WHERE screeps_id=%s"
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(query, (token, datetime.datetime.utcnow(), id))
            conn.commit()
        return (id, token)
