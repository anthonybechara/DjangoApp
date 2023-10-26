from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# @receiver(user_logged_in)
# def user_logged_in_handler(sender, request, user, **kwargs):
#     user.is_online = True
#     user.save()


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    # user.is_online = False
    user.last_logout = timezone.now()
    user.save()

