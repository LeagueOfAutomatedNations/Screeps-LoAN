#!/usr/bin/env python
from migrate.versioning.shell import main
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    db_url = "postgresql://%s:5432/%s?user=%s&password=%s" % (
        os.environ["DB_HOST"],
        os.environ["DB"],
        os.environ["DB_USERNAME"],
        os.environ["DB_PASSWORD"],
    )
    main(url=db_url, repository="db", debug="False")
