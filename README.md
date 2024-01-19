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
flask import-users
flask import-rankings
flask import-user-rankings
```

You can restore a database from a backup file like if the following file exist, replace YOUR_PASSWORD with your db password.
```bash
docker-compose exec -e POSTGRES_HOST='postgres' -e POSTGRES_PASS='YOUR_PASSWORD' -e TARGET_ARCHIVE='/backups/2024/January/PG_screeps.15-January-2024.dmp' -e TARGET_DB='screeps_backup' pgbackups /backup-scripts/restore.sh
```