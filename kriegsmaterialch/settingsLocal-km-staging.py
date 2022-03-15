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

ALLOWED_HOSTS = ['staging.kriegsmaterial.ch']

# SECURITY WARNING: keep the secret key used in production secret!
# just generate an arbitrary string of similar strength to replace this!
# for example pwgen -sy 60
SECRET_KEY = """5C&qJ[vucK~{fBjs/>LTK+_/G"\cX^{&BO.K)waB&C:>B_I?#{O(;0Jc'v:]"""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'export-stat-staging',
        'HOST' : 'localhost',
        'USER' : 'export-stat-staging',
        'PASSWORD' : 'zaV2Aif1withooz8rae8',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/lamp0/web/vhosts/default/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/lamp0/web/vhosts/default/media/'
