"""
WSGI config for NH project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""
import sys
import os

from django.core.wsgi import get_wsgi_application
from django.core.handlers.wsgi import WSGIHandler
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'NH.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NH.settings")
application = get_wsgi_application()
