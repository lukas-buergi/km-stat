"""
Modified to suit architecture imposed by hosting provider: Moved to root directory of project.
WSGI config for kriegsmaterialch project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'kriegsmaterialch')))
# the above code is to enable this file to run in root directory of project instead of kriegsmaterialch subdirectory.

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriegsmaterialch.settings')

application = get_wsgi_application()
