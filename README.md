# Requirements

- Postgres
- Python 3.x

# Setup

```bash
cp .env.example .env
nano .env # add api settings.
```

Then `docker compose up -d` should be enough to start the web app, and it should be browsable at http://localhost:5000/

Once you've done that, log into the container with `docker compose exec loan bash` and
run the following to initalize the postgres database:

```bash
python db/manage.py version_control
python db/manage.py upgrade
```

Finally, you can populate the database by doing this:

```bash
flask import_users
flask import_rankings
flask import_alliances
flask import_user_rankings
```
