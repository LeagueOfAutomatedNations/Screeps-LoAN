import datetime
import hashlib
import os

import screeps_loan.models.users as users_model
import screeps_loan.services.users as users_service
from screeps_loan.models.db import get_conn


class AuthPlayer(object):
    def __init__(self, api_client):
        self.api_client = api_client

    def random_token(self):
        return hashlib.sha512(os.urandom(128)).hexdigest()[0: 15]

    def id_from_name(self, name):
        id = users_model.player_id_from_db(name)
        if id is None:
            id = users_service.player_id_from_api(name)
            users_model.insert_username_with_id(name, id)
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
        return id, token
