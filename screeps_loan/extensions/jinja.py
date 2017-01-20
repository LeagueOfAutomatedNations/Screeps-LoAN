from screeps_loan import app
import screeps_loan.models.alliances as alliances_model

alliance_query = alliances_model.AllianceQuery()
app.jinja_env.globals.update(get_name_from_shortname=alliance_query.find_by_shortname)
