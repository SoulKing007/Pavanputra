
from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lk0mr&b=xm+fve1v+e@v_y*y*rukn7ktc9e#ndujf1cy&h(_^j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'viewflow',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pavanputra',
    'myapp',
    'accounts',
    'widget_tweaks',
    
]
CRISPY_TEMPLATE_PACK = 'bootstrap4'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
   # 'livereload.middleware.LiveReloadScript', 
]

ROOT_URLCONF = 'pavanputra.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  
        
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

WSGI_APPLICATION = 'pavanputra.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
        'timeout': 20,
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATICFILES_DIRS = [
    BASE_DIR / 'static/assets',  # Path to the assets folder
]


STATICFILES_DIRS = [
    BASE_DIR / 'static',  
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'myapp.CustomUser'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # Use 'apikey' as the username
EMAIL_HOST_PASSWORD = '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'  # SendGrid API key
DEFAULT_FROM_EMAIL = 'niravthapa@gmail.com'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {
    messages.ERROR: 'alert-danger',
    messages.SUCCESS: 'alert-success',
}

LOGOUT_REDIRECT_URL = '/'

LOGIN_URL = '/login/'


STRIPE_PUBLISHABLE_KEY = "pk_test_51R1ABjHTwys1pMyVvVduemoM8zfTen5AfokZ3mt47yqFJsq67p7RIWiRCEMwAs16Ccs32mwbgALJD3IwVzUkks8g00rHTNpeHf"
STRIPE_SECRET_KEY = "sk_test_51R1ABjHTwys1pMyVG5PicOk7s60KjEQladC2rrUSPffufmY3klUSpBftxTKKsBR4JPewEwfSnaIY6m5MMMQDQ9YD00eMqc27OR"

APP_URL="http://127.0.0.1:8000/"