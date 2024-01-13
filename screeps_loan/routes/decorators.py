import datetime
import time
from functools import wraps
from flask import redirect, url_for, session, make_response
from wsgiref.handlers import format_date_time


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "my_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def httpresponse(expires=None, round_to_minute=False, content_type="text/html"):
    def cache_decorator(view):
        @wraps(view)
        def cache_func(*args, **kwargs):
            now = datetime.datetime.now()

            response = make_response(view(*args, **kwargs))
            response.headers["Content-Type"] = content_type
            response.headers["Last-Modified"] = format_date_time(
                time.mktime(now.timetuple())
            )

            if expires is None:
                response.headers[
                    "Cache-Control"
                ] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
                response.headers["Expires"] = "-1"
            else:
                expires_time = now + datetime.timedelta(seconds=expires)

                if round_to_minute:
                    expires_time = expires_time.replace(second=0, microsecond=0)

                response.headers["Cache-Control"] = "public, max-age=%s" % (
                    expires * 4,
                )
                response.headers["Expires"] = format_date_time(
                    time.mktime(expires_time.timetuple())
                )

            return response

        return cache_func

    return cache_decorator
