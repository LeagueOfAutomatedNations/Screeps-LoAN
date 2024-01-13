import click
from screeps_loan import app
import screepsapi.screepsapi as screepsapi
from screeps_loan.models.db import get_conn
from screeps_loan.screeps_client import get_client
from screeps_loan.models import db
from screeps_loan.services.cache import cache

import screeps_loan.models.alliances as alliances
import screeps_loan.models.users as users

from random import shuffle, random
from time import sleep
import math


POWER_POW = 1.15
POWER_MULTIPLY = 1000
POWER_MAX = 750

powertotals = [{"level": 0, "total": 0}]
powerlevels = {}
total = 0

for i in range(0, POWER_MAX):
    needed = math.pow(i, POWER_POW) * POWER_MULTIPLY
    total += needed
    powertotals.append({"level": i, "total": total})
    powerlevels[i] = total

powertotals = list(reversed(powertotals))


@cache.cache("getUserControlPoints")
def getUserControlPoints(username):
    user_info = getUserInfo(username)
    if not user_info:
        return 1
    if "user" in user_info:
        if "gcl" in user_info["user"]:
            return user_info["user"]["gcl"]
    return 1


@cache.cache("getUserPowerPoints")
def getUserPowerPoints(username):
    user_info = getUserInfo(username)
    if not user_info:
        return 1
    if "user" in user_info:
        if "power" in user_info["user"]:
            return user_info["user"]["power"]
    return 0


@cache.cache("getUserInfo")
def getUserInfo(username):
    screeps = get_client()
    sleep(1)
    return screeps.user_find(username)


class Rankings(object):
    gclcache = {}

    def run(self):
        alliance_query = alliances.AllianceQuery()
        all_alliances = alliance_query.getAll()
        alliances_names = [item["shortname"] for item in all_alliances]
        users_with_alliance = users.UserQuery().find_name_by_alliances(alliances_names)

        query = "SELECT id FROM room_imports WHERE status LIKE 'complete' ORDER BY started_at DESC"
        result = db.find_one(query)
        self.room_import_id = result[0]

        self.conn = get_conn()
        self.start()
        print(self.id)

        for alliance in all_alliances:
            users_with_alliance = self.find_name_by_alliances(alliances_names)
            members = [
                user["name"]
                for user in users_with_alliance
                if user["alliance"] == alliance["shortname"]
            ]
            filtered_members = [
                user for user in members if self.get_player_room_count(user) > 0
            ]

            # Not enough members.
            if len(filtered_members) < 2:
                continue

            # Not enough rooms
            if self.get_room_count(alliance["shortname"]) < 2:
                continue

            rcl = self.getAllianceRCL(alliance["shortname"])

            combined_gcl = sum(self.getUserGCL(user) for user in filtered_members)
            average_gcl = combined_gcl / len(filtered_members)
            control = sum(getUserControlPoints(user) for user in filtered_members)
            alliance_gcl = self.convertGcl(control)

            combined_power = sum(
                self.getUserPowerLevel(user) for user in filtered_members
            )
            power = sum(getUserPowerPoints(user) for user in filtered_members)
            alliance_power = self.convertPowerToLevel(power)

            spawns = self.getAllianceSpawns(alliance["shortname"])
            print(
                "%s- %s, %s, %s, %s, %s, %s, %s, %s"
                % (
                    alliance["shortname"],
                    combined_gcl,
                    average_gcl,
                    alliance_gcl,
                    rcl,
                    spawns,
                    len(filtered_members),
                    alliance_power,
                    combined_power,
                )
            )

            self.update(
                alliance["shortname"],
                alliance_gcl,
                combined_gcl,
                average_gcl,
                rcl,
                spawns,
                len(filtered_members),
                alliance_power,
                combined_power,
            )

        self.finish()
        self.conn.commit()

    def start(self):
        query = (
            "INSERT INTO rankings_imports(status) VALUES ('in progress') RETURNING id"
        )
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.id = cursor.fetchone()[0]

    def finish(self):
        query = "UPDATE rankings_imports SET status='complete' WHERE id=(%s)"
        cursor = self.conn.cursor()
        cursor.execute(query, (self.id,))

    def update(
        self,
        alliance,
        alliance_gcl,
        combined_gcl,
        average_gcl,
        rcl,
        spawns,
        members,
        alliance_power,
        combined_power,
    ):
        # Store info in db
        cursor = self.conn.cursor()
        query = "INSERT INTO rankings(import, alliance, alliance_gcl, combined_gcl, average_gcl, rcl, spawns, members, alliance_power, combined_power) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(
            query,
            (
                self.id,
                alliance,
                alliance_gcl,
                combined_gcl,
                average_gcl,
                rcl,
                spawns,
                members,
                alliance_power,
                combined_power,
            ),
        )

    def getAllianceRCL(self, alliance):
        query = "SELECT SUM(level) FROM rooms, users WHERE rooms.owner = users.id AND users.alliance=%s AND rooms.import=%s"
        cursor = self.conn.cursor()
        cursor.execute(query, (alliance, self.room_import_id))
        result = cursor.fetchone()[0]
        if result is not None:
            return result
        return 0

    def getAllianceSpawns(self, alliance):
        count = 0
        query = "SELECT COUNT(*) FROM rooms, users WHERE rooms.owner = users.id AND users.alliance=%s AND level>=8 AND rooms.import=%s"
        cursor = self.conn.cursor()
        cursor.execute(query, (alliance, self.room_import_id))
        result = cursor.fetchone()[0]
        if result is not None:
            if result:
                count += result * 3

        query = "SELECT COUNT(*) FROM rooms, users WHERE rooms.owner = users.id AND users.alliance=%s AND level=7 AND rooms.import=%s"
        cursor = self.conn.cursor()
        cursor.execute(query, (alliance, self.room_import_id))
        result = cursor.fetchone()[0]
        if result is not None:
            if result:
                count += result * 2

        query = "SELECT COUNT(*) FROM rooms, users WHERE rooms.owner = users.id AND users.alliance=%s AND level>=1 AND level<7 AND rooms.import=%s"
        cursor = self.conn.cursor()
        cursor.execute(query, (alliance, self.room_import_id))
        result = cursor.fetchone()[0]
        if result is not None:
            if result:
                count += result

        return count

    def convertGcl(self, control):
        return int((control / 1000000) ** (1 / 2.4)) + 1

    def getUserGCL(self, username):
        return self.convertGcl(getUserControlPoints(username))

    def convertPowerToLevel(self, power):
        if power <= 0:
            return 0
        for powerdata in powertotals:
            if powerdata["total"] < power:
                return powerdata["level"]
        return 0

    def getUserPowerLevel(self, username):
        return self.convertPowerToLevel(getUserPowerPoints(username))

    def find_name_by_alliances(self, alliance):
        query = "SELECT ign, alliance FROM users where alliance = ANY(%s)"
        cursor = self.conn.cursor()
        cursor.execute(query, (alliance,))
        result = cursor.fetchall()
        return [{"name": row[0], "alliance": row[1]} for row in result]

    def get_room_count(self, alliance):
        query = """
        SELECT COUNT(DISTINCT rooms.name)
            FROM rooms,users
            WHERE rooms.owner=users.id
                AND users.alliance=%s
                AND rooms.import = (SELECT id
                                        FROM room_imports
                                        ORDER BY id desc
                                        LIMIT 1
                                    );
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (alliance,))
        result = cursor.fetchone()
        return int(result[0])

    def get_player_room_count(self, player):
        query = """
        SELECT COUNT(DISTINCT rooms.name)
              FROM rooms,users
              WHERE rooms.owner=users.id
                  AND users.ign=%s
                  AND rooms.import = (SELECT id
                                          FROM room_imports
                                          ORDER BY id desc
                                          LIMIT 1
                                      );
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (player,))
        result = cursor.fetchone()
        return int(result[0])


@app.cli.command()
def import_rankings():
    click.echo("Generating Rankings")
    r = Rankings()
    r.run()


@app.cli.command()
def import_user_rankings():
    click.echo("Generating User Rankings")
    dbusers = users.get_all_users_for_importing()
    for dbuser in dbusers:
        # Only retrieve information if we don't have any or the player has some active rooms.
        if (
            not dbuser["gcl"]
            or users.get_player_room_count(dbuser["ign"]) > 0
            or random() < 0.05
        ):
            gcl = getUserControlPoints(dbuser["ign"])
            power = getUserPowerPoints(dbuser["ign"])
            gcl_level = users.convertGcl(gcl)
            rcl = users.getUserRCL(dbuser["id"])
            spawns = users.getUserSpawns(dbuser["id"])

            print(
                "%s has %s gcl and %s power, gclLevel %s, rcl %s, spawns %s"
                % (dbuser["ign"], gcl, power, gcl_level, rcl, spawns)
            )
            users.update_gcl_by_user_id(
                dbuser["id"], getUserControlPoints(dbuser["ign"])
            )
            users.update_power_by_user_id(
                dbuser["id"], getUserPowerPoints(dbuser["ign"])
            )
            users.update_gcl_level_by_user_id(dbuser["id"], gcl_level)
            users.update_combined_rcl_by_user_id(dbuser["id"], rcl)
            users.update_spawncount_by_user_id(dbuser["id"], spawns)
            sleep(1.5)
        else:
            print("Skipping user %s" % (dbuser["ign"]))
