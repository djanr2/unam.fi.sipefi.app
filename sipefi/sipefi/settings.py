"""
Django settings for sipefi project.

Generated by 'django-admin startproject' using Django 5.2.3.

"""
import os

from pathlib import Path
#funcion para desencriptar datos conexion de la base de datos
from cryptography.fernet import Fernet

def desencripta(texto, key):
    texto = texto.encode()
    key = key.encode()
    fer = Fernet(key)
    return fer.decrypt(texto).decode()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5x9#a*z8a4!v-0r0i(1a@6z4wd3yj-i(+rb(#$xd1kb(om2dtz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sipefi_apps.principal.controlador.MiddlewareHttp.MiddlewareHttpReqResp'
]

ROOT_URLCONF = 'sipefi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"vistas")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sipefi.wsgi.application'


# Database
f = open(os.path.join(BASE_DIR,"connectionDjango.txt"), "r") 
dataDB = f.read().split("*##@@##*")
key = dataDB[0]
host = desencripta(dataDB[2], key)
port = desencripta(dataDB[3], key)
service = desencripta(dataDB[1], key)

DATABASES = {
    'default': {
    'ENGINE':   'django.db.backends.oracle',
    'NAME':     f"{host}:{port}/{service}",
    'USER':     desencripta(dataDB[4],key),
    'PASSWORD': desencripta(dataDB[5],key),
    'CONN_MAX_AGE': 1800,  # 30 minutos despues de conexion inactiva
  }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True

DATE_FORMAT = 'd/m/Y'  # Ejemplo: 25/06/2025
TIME_FORMAT = 'H:i:s'  # Ejemplo: 14:30:45
DATETIME_FORMAT = 'd/m/Y H:i:s'  # Ejemplo: 25/06/2025 14:30:45


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/estaticos/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'estaticos'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
