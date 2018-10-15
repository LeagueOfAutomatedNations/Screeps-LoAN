import os
import subprocess
from datetime import datetime, timedelta

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


@app.cli.command()
def purge_cdn():
    if 'CACHE_ROOT' not in app.config:
        return

    staticdir = app.root_path + '/static'
    dirlen = len(app.root_path)
    print(staticdir)
    for dirpath, dirnames, filenames in os.walk(staticdir):
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            url = app.config['WEB_ROOT'] + fullpath[dirlen:]
            print(url)
            subprocess.call(['curl', '-X', 'PURGE', url])
