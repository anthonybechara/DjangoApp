import logging
from typing import Callable
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model, logout
from django.contrib.messages import info

from .utils import now, seconds_until_idle_time_end, seconds_until_session_end

UserModel = get_user_model()
logger = logging.getLogger(__name__)


def _auto_logout(request, options):
    should_logout = False
    current_time = now()

    if request.user.is_authenticated:

        session_identifier = str(request.session.get('unique_session_id'))
        session_time = request.session.get('session_time')
        idle_time = request.session.get('idle_time')

        if session_time is not None and idle_time is not None:
            session_key = f'session_end_{session_identifier}'
            session_time_remaining = seconds_until_session_end(request, current_time)
            idle_time_remaining = seconds_until_idle_time_end(request, idle_time, current_time)

            should_logout |= (session_time_remaining < 0) and (idle_time_remaining < 0)

            if should_logout and request.session.get(session_key):
                del request.session[session_key]
            else:
                request.session[session_key] = current_time.isoformat()

        elif idle_time is not None:
            idle_key = f'idle_end_{session_identifier}'
            idle_time_remaining = seconds_until_idle_time_end(request, idle_time, current_time)

            should_logout |= idle_time_remaining < 0

            if should_logout and request.session.get(idle_key):
                del request.session[idle_key]
            else:
                request.session[idle_key] = current_time.isoformat()

    if should_logout:
        logger.debug('Logout user %s', request.user)
        logout(request)

        if 'MESSAGE' in options:
            info(request, options['MESSAGE'], extra_tags='session-expire')


def auto_logout(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable:
    def middleware(request: HttpRequest) -> HttpResponse:
        if not request.user.is_anonymous and hasattr(settings, 'AUTO_LOGOUT'):
            _auto_logout(request, settings.AUTO_LOGOUT)

        return get_response(request)

    return middleware
