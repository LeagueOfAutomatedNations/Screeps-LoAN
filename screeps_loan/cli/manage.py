import click
from screeps_loan import app
from screeps_loan.models import users
import screepscriptions.services.screepsclient as screeps_client
from screepscriptions.models.authuser import AuthPlayer


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
