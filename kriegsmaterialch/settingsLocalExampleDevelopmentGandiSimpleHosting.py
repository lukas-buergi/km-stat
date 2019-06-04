
ALLOWED_HOSTS = [       '83f4738c4e5247f88ee107fd4add919e.yatu.ws',
                        'ahch4chaiw1ofieg4ain.t4b.me'
                ]

# SECURITY WARNING: keep the secret key used in production secret!
# just generate an arbitrary string of similar strength to replace this!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'export-stat-staging',
        'HOST' : 'localhost',
        'USER' : 'export-stat-staging',
        'PASSWORD' : '',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/lamp0/web/vhosts/default/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/lamp0/web/vhosts/default/media/'
