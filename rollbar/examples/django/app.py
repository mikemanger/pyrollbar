import os
import sys

from django.conf import settings
from django.http import HttpResponse
from django.urls import path


ROLLBAR_CONFIG = {
    'access_token': 'POST_SERVER_ITEM_ACCESS_TOKEN',
    'environment': 'development',
    'branch': 'master',
    'root': os.getcwd()
}

MIDDLEWARE_CONFIG = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Rollbar middleware
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
)

settings.configure(
    DEBUG=True,
    SECRET_KEY='thisisthesecretkey',
    ROOT_URLCONF=__name__,
    ROLLBAR = ROLLBAR_CONFIG,
    MIDDLEWARE = MIDDLEWARE_CONFIG,
)

def index(request):
    return HttpResponse('Hello World')

def error(request):
    foo()
    return HttpResponse('You shouldn\'t be seeing this')


urlpatterns = (
    path('', index),
    path('error', error),
)

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
