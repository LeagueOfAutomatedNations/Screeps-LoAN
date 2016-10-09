import os, sys
from datetime import datetime, timedelta
from subprocess import call
import click
from screeps_loan import app


@app.cli.command()
def clean_sessions():
    sessiondir = app.config['CACHE_ROOT'] + '/sessions'
    for dirpath, dirnames, filenames in os.walk(sessiondir):
        for file in filenames:
            curpath = os.path.join(dirpath, file)
            file_modified = datetime.fromtimestamp(os.path.getmtime(curpath))
            if datetime.now() - file_modified > timedelta(hours=336):
                os.remove(curpath)


def get_file_directory(file):
    return os.path.dirname(os.path.abspath(file))
