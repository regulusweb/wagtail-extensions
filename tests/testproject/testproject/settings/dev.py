from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(4w@q+x#w3(w(fbp+0e@49him4zp+$6h$*7ac9-hv&m^9uedi)'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MANAGERS = [
    ('admin', 'admin@localhost.com')
]

EMAIL_SUBJECT_PREFIX = 'Admin'

try:
    from .local import *
except ImportError:
    pass
