from datetime import timedelta
from django.utils import timezone


class RememberMeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and 'just_logged_in' in request.session:
            remember_me = request.session.get('remember_me')
            if remember_me:
                session_time = timezone.now() + timedelta(days=105)
                request.session['session_time'] = 7775800
                request.session['idle_time'] = 10790
                request.session.set_expiry(session_time)

                # settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
            else:
                idle_time = timezone.now() + timedelta(hours=3)
                request.session['idle_time'] = 10790
                request.session.set_expiry(idle_time)

                # settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True

            request.session['unique_session_id'] = request.session.session_key
            del request.session['just_logged_in']

        response = self.get_response(request)
        return response
