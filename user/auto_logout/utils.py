from datetime import datetime, timedelta
from typing import Union
from django.http import HttpRequest
from django.utils.timezone import now

now = now


def seconds_until_session_end(request: HttpRequest, current_time: datetime) -> float:

    session_identifier = str(request.session.get('unique_session_id'))
    session_key = f'session_end_{session_identifier}'

    if session_key in request.session:
        return (request.session.get_expiry_date() - current_time - timedelta(seconds=3)).total_seconds()
    else:
        return 0.0


def seconds_until_idle_time_end(request: HttpRequest, idle_time: Union[int, timedelta],
                                current_time: datetime) -> float:

    if isinstance(idle_time, timedelta):
        ttl = idle_time
    elif isinstance(idle_time, int):
        ttl = timedelta(seconds=idle_time)
    else:
        raise TypeError(f"AUTO_LOGOUT['idle_time'] should be `int` or `timedelta`, "
                        f"not `{type(idle_time).__name__}`.")

    session_identifier = str(request.session.get('unique_session_id'))
    idle_key = f'idle_end_{session_identifier}'
    session_key = f'session_end_{session_identifier}'

    if idle_key in request.session:
        last_req = datetime.fromisoformat(request.session[idle_key])
        request.session.set_expiry(last_req + timedelta(hours=3))

    elif session_key in request.session:
        if request.session.get_expiry_date() - datetime.fromisoformat(request.session[session_key]) < timedelta(
                hours=3):
            request.session.set_expiry(datetime.fromisoformat(request.session[session_key]) + timedelta(hours=3))
        last_req = datetime.fromisoformat(request.session[session_key])
    else:
        last_req = current_time

    return (last_req - current_time + ttl).total_seconds()
