from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver


@receiver(user_logged_in)
def Login(sender, request, user, **kwargs):
    print('user {} logged in through {}'.format(user.username, request.META.get('HTTP_REFERER')))

@receiver(user_login_failed)
def loginFailed(sender, credentials, user, request, **kwargs):
    print('user {} failed to log in through {}'.format(user.username, request.META.get('HTTP_REFERER')))

@receiver(user_logged_out)
def Logout(sender, request, user, **kwargs):
    print('user {} logged out through {}'.format(user.username, request.META.get('HTTP_REFERER')))