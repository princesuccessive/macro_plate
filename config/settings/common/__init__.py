# -----------------------------------------------------------------------------
# General Django Configuration Starts Here
# -----------------------------------------------------------------------------

from .authentication import *
from .business_logic import *
from .cacheops import *
from .celery import *
from .cors import *
from .databases import *
from .drf import *
from .general import *
from .installed_apps import *
from .internationalization import *
from .logging import *
from .messages import *
from .middleware import *
from .paths import *
from .security import *
from .static import *
from .storage import *
from .templates import *
from .testing import *

SITE_ID = 1
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

ADMINS = (
    ('Macroplate Admins', 'macroplate@saritasa.com'),
)

MANAGERS = ADMINS
