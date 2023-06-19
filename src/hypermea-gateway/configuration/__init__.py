import os
import socket

from . import settings

VERSION = '0.1.0'


# set environment variables from _env.conf (which is in .gitignore)
if os.path.exists('_env.conf'):
    with open('_env.conf') as setting:
        for line in setting:
            if not line.startswith('#'):
                line = line.rstrip()
                nvp = line.split('=')
                if len(nvp) == 2:
                    os.environ[nvp[0].strip()] = nvp[1].strip()


SETTINGS = settings.Settings.instance()
SETTINGS.set_prefix_description('HY', 'HypermeaService base configuration')
SETTINGS.create('HY', {
    'API_NAME': 'hypermea-gateway',

    'MONGO_ATLAS': 'Disabled',
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'hypermea-gateway',
    'API_PORT': 2112,
    'INSTANCE_NAME': socket.gethostname(),
    'TRACE_LOGGING': 'Enabled',
    'PAGINATION_LIMIT': 3000,
    'PAGINATION_DEFAULT': 1000,
    'ADD_ECHO': 'Disabled',
    'LOG_TO_FOLDER': 'Disabled',
    'SEND_ERROR_EMAILS': 'Disabled',
})

# optional settings...
SETTINGS.create('HY', 'BASE_URL', is_optional=True)
SETTINGS.create('HY', 'GATEWAY_URL', is_optional=True)
SETTINGS.create('HY', 'NAME_ON_GATEWAY', is_optional=True)
SETTINGS.create('HY', 'URL_PREFIX', is_optional=True)
SETTINGS.create('HY', 'CACHE_CONTROL', is_optional=True)
SETTINGS.create('HY', 'CACHE_EXPIRES', is_optional=True, default_value=0)
SETTINGS.create('HY', 'MONGO_USERNAME', is_optional=True)
SETTINGS.create('HY', 'MONGO_PASSWORD', is_optional=True)
SETTINGS.create('HY', 'MONGO_AUTH_SOURCE', is_optional=True)
SETTINGS.create('HY', 'MEDIA_BASE_URL', is_optional=True)
SETTINGS.create('HY', 'PUBLIC_RESOURCES', is_optional=True)

if SETTINGS.has_enabled('HY_SEND_ERROR_EMAILS'):
    SETTINGS.create('HY', 'SMTP_PORT', default_value=25)
    SETTINGS.create('HY', 'SMTP_HOST', is_optional=True)
    SETTINGS.create('HY', 'ERROR_EMAIL_RECIPIENTS', is_optional=True)
    SETTINGS.create('HY', 'ERROR_EMAIL_FROM', is_optional=True)

# cancellable settings...
# if SETTINGS.get('HY_CANCELLABLE') == '':
#     del SETTINGS['HY_CANCELLABLE']