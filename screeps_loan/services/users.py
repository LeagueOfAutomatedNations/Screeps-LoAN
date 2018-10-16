from screeps_loan.screeps_client import get_client

def player_id_from_api(name):
    screeps = get_client()
    resp = screeps.user_find(name)
    if ((resp['ok'] == 1) and (resp['user'] is not None)):
        return resp['user']['_id']
    return None
