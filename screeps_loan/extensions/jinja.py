from flask import session
from screeps_loan import app
import screeps_loan.models.alliances as alliances_model
from screeps_loan.screeps_client import get_client
from screeps_loan.services.cache import cache

alliance_query = alliances_model.AllianceQuery()
app.jinja_env.globals.update(get_name_from_alliance_id=alliance_query.find_by_id)


import screeps_loan.models.users as users

app.jinja_env.globals.update(get_name_from_user_id=users.user_name_from_db_id)
app.jinja_env.globals.update(get_shortname_from_alliance_id=alliances_model.find_shortname_by_id)


import screeps_loan.models.invites as invites


def user_has_invites():
    my_invites = invites.get_invites_by_user(session["my_id"])
    return len(my_invites) > 0


app.jinja_env.globals.update(has_invites=user_has_invites)


@cache.cache()
def get_shards():
    api = get_client()
    shards = api.get_shards()
    if not shards:
        shards = ["shard"]
    return shards


app.jinja_env.globals.update(shard_list=get_shards)
