#######################################################################
# Copyright Lukas Bürgi 2019
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

ALLOWED_HOSTS = [ 'alohcheigee0ou7ooqu3.t4b.me' ]

# SECURITY WARNING: keep the secret key used in production secret!
# just generate an arbitrary string of similar strength to replace this!
SECRET_KEY = '77j1FoPOl3ZohEJT8JoGBHLiPhVBG2Kp4Dbpjx1WViw7TKvTyD4d331hxJQoSVBM'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'kriegsmaterialch',
        'HOST' : 'localhost',
        'USER' : 'kriegsmaterialch',
        'PASSWORD' : 'Ze5uukaephooth3aivah',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = 'https://static.alohcheigee0ou7ooqu3.t4b.me/'
STATIC_ROOT = '/var/www/km-stat/static/'

MEDIA_URL = 'https://media.alohcheigee0ou7ooqu3.t4b.me/'
MEDIA_ROOT = '/var/www/km-stat/media/'
