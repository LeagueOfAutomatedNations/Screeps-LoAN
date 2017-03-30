import click
from screeps_loan import app
import screepsapi.screepsapi as screepsapi
import re
from screeps_loan.models.db import get_conn
from screeps_loan.screeps_client import get_client

class Map(object):
    roomRegex = re.compile(r'(E|W)(\d+)(N|S)(\d+)')
    queueLimit = 1000
    worldSize = 100

    def getRoomData(self, room):
        match = self.roomRegex.match(room)
        data = {}
        data['x_dir'] = match.group(1)
        data['x'] = int(match.group(2))
        data['y_dir'] = match.group(3)
        data['y'] = int(match.group(4))
        return data

    def isNPC(self, room):
        data = self.getRoomData(room)

        x = data['x']
        y = data['y']

        if x == 0 or y == 0:
            return True

        if x % 10 == 0:
            return True

        if y % 10 == 0:
            return True

        if x % 5 == 0 and y % 5 == 0:
            return True

        if x % 10 <= 3 or x % 10 >= 7:
            return False

        if y % 10 <= 3 or y % 10 >= 7:
            return False

        return True

    def run(self):
        self.start()
        api = get_client()
        queue = []
        user_map = {}
        roomCount = 0;
        for x in range(1, self.worldSize + 1):
            for y in range(1, self.worldSize + 1):
                for horizontal in ['E', 'W']:
                    for vertical in ['N', 'S']:
                        room = "%s%s%s%s" % (horizontal, x, vertical, y)
                        if self.isNPC(room):
                            continue
                        queue.append(room)
                if len(queue) < self.queueLimit:
                    if y < self.worldSize or x < self.worldSize:
                        continue
                room_statistics = api.map_stats(queue, 'claim0')
                roomCount += self.queueLimit
                click.echo(str(roomCount) + " rooms requested")
                #self.calls = self.calls + 1
                queue = []

                for id, user_info in room_statistics['users'].items():
                    username = user_info['username']
                    user_map[id] = username

                for room, statistics in room_statistics['stats'].items():
                    if 'own' in statistics:
                        if 'user' in statistics['own']:
                            user_id = statistics['own']['user']
                            level = statistics['own']['level']
                            self.update(user_id, user_map[user_id], room, level)

        conn = get_conn()
        self.finish()
        conn.commit()

    def start(self):
        query = "INSERT INTO room_imports(status) VALUES ('in progress') RETURNING id"
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(query)
        self.id = cursor.fetchone()[0]

    def finish(self):
        # import, timestamp, status
        query = "UPDATE room_imports SET status='complete' WHERE id=(%s)"
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(query, (self.id, ))

    def clear(self):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rooms;")

    def update(self, user_id, username, room, level):
        # Store info in db
        query = "SELECT id FROM users WHERE screeps_id = %s"
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(query, (user_id, ))
        row = cursor.fetchone()
        if (row is None):
            query = "INSERT INTO users(ign, screeps_id) VALUES (%s, %s) RETURNING id"
            cursor.execute(query, (username, user_id))
            id = cursor.fetchone()[0]
        else:
            id = row[0]

        query = "INSERT INTO rooms(import, name, level, owner) VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (self.id, room, level, id))


@app.cli.command()
def import_users():
    click.echo("Start to import users from Screeps API")
    m = Map()
    m.run()


@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo('Init the db')

@app.cli.command()
def import_alliances():
    click.echo("Start to import alliances from http://www.leagueofautomatednations.com/alliances.js")
    import requests as r
    import json
    import screeps_loan.models.alliances as alliances_model
    import screeps_loan.models.users as users_model
    import screeps_loan.auth_user
    import screeps_loan.services.users as users_service

    alliance_query = alliances_model.AllianceQuery()
    users_query = users_model.UserQuery()
    screeps = get_client()
    auth_user = screeps_loan.auth_user.AuthPlayer(screeps)
    resp = r.get('http://www.leagueofautomatednations.com/alliances.js')
    data = json.loads(resp.text)
    for shortname, info in data.items():
        members = info['members']
        fullname = info['name']
        color = None
        if 'color' in info:
            color = info['color']
        slack = None
        if 'slack' in info:
            slack = info['slack']
        alliance = alliance_query.find_by_shortname(shortname)
        if (alliance is None):
            alliance_query.insert_alliance(shortname, fullname, color, slack)
            alliance = shortname

        existing_member = [i['name'] for i in users_query.find_name_by_alliances([shortname])]
        new_members = [name for name in members if name not in existing_member]
        for member in new_members:
            id = users_service.player_id_from_api(member)
            users_query.update_alliance_by_screeps_id(id, shortname)
