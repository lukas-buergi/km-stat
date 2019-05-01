
ALLOWED_HOSTS = [ 'alohcheigee0ou7ooqu3.t4b.me' ]

# SECURITY WARNING: keep the secret key used in production secret!
# just generate an arbitrary string of similar strength to replace this!
SECRET_KEY = 'l#9ts+=wbie*^bu#1e-zyzero$*@5-!edo@qw_hpa_0t3f7c+o'

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
