ALLOWED_HOSTS = ['d9408ee71d4f4b3aa363bbe592098b4f.testing-url.ws']

# SECURITY WARNING: keep the secret key used in production secret!
# just generate an arbitrary string of similar strength to replace this!
# for example pwgen -sy 60
SECRET_KEY = 'lBE{Bk,0rIR8gj?L6D8|@4(d0,M85Fu}yUyY:2)q$)\;.-Y,wv%@|N&k:'

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
        'PASSWORD' : '6nWEV7V4GqYgADm',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/lamp0/web/vhosts/default/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/lamp0/web/vhosts/default/media/'
