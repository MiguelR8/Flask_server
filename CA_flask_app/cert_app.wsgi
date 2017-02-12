#Source: http://flask.pocoo.org/docs/0.11/deploying/mod_wsgi/

import os
from config import activate_venv
activate_venv()

from app import app as application