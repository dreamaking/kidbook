import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'sites.production'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()