from screeps_loan import app
from flask import render_template
import screeps_loan.models.users as users

gcl_min = 1000000
power_min = 100000
combined_min = 1000000


@app.route("/player/rankings/gcl")
def player_rankings_gcl():
    userlist = [
        elem
        for elem in users.get_all_users()
        if isinstance(elem["gcl"], int) and elem["gcl"] > gcl_min
    ]
    userlist.sort(key=lambda a: a["gcl"])
    return render_template(
        "user_rankings.html", rankings=userlist[::-1], field="gcl", category="GCL"
    )


@app.route("/player/rankings/power")
def player_rankings_power():
    userlist = [
        elem
        for elem in users.get_all_users()
        if isinstance(elem["power"], int) and elem["power"] > power_min
    ]
    userlist.sort(key=lambda a: a["power"])
    return render_template(
        "user_rankings.html", rankings=userlist[::-1], field="power", category="Power"
    )


@app.route("/player/rankings/complete")
def player_rankings_combined():
    userlist = users.get_all_users()
    finalusers = []
    for user in userlist:
        combined = 0
        if "power" in user and isinstance(user["power"], int):
            combined += user["power"] * 50

        if "gcl" in user and isinstance(user["gcl"], int):
            combined += user["gcl"]

        if combined > combined_min:
            finalusers.append({"ign": user["ign"], "combined": combined})
    finalusers.sort(key=lambda a: a["combined"])
    return render_template(
        "user_rankings.html",
        rankings=finalusers[::-1],
        field="combined",
        category="Combined",
    )
