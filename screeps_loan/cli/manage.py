import click
from screeps_loan import app
from screeps_loan.models import users
import screeps_loan.screeps_client as screeps_client
from screeps_loan.auth_user import AuthPlayer


import screeps_loan.models.alliances as alliances_model



@app.cli.command()
@click.argument('user')
def clear_user_alliance(user):
    user = users.player_id_from_db(user)
    if user:
        users.update_alliance_by_screeps_id(user, None)


@app.cli.command()
@click.argument('user')
def login_as_user(user):
    api = screeps_client.get_client()
    auth = AuthPlayer(api)
    (id, token) = auth.auth_token(user)
    if (id is not None):
        message = "%s/auth/%s" % (app.config['WEB_ROOT'], token)
        click.echo(message)


@app.cli.command()
@click.argument('alliance')
def room_count(alliance):
    click.echo(alliances_model.get_room_count(alliance))
