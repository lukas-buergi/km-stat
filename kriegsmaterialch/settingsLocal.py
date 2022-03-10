#######################################################################
# Copyright Lukas Bürgi 2022
#
# This file is part of km-stat.
#
# km-stat is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# km-stat is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with km-stat.  If not, see
# <https://www.gnu.org/licenses/>.
########################################################################

"""
settingsLocal.py file for use with docker. Replace this with one of the examples also in this directoy when not running docker.
"""

import os

# SECURITY WARNING: keep the secret key used in production secret!
# just generate an arbitrary string of similar strength to replace this!
SECRET_KEY = 'l#9ts+=wbie*^bu#1e-zyzero$*@5-!edo@qw_hpa_0t3f7c+o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST' : os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_DATABASE'),
        'USER' : os.environ.get('DB_USER'),
        'PASSWORD' : os.environ.get('DB_PASSWORD'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = '/code/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = 'media/'