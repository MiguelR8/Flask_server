#Credit to https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database

try:
	from migrate.versioning import api
except ImportError:
	from config import activate_venv
	activate_venv()
	from migrate.versioning import api
	
from config import SQLALCHEMY_DATABASE_URI as db_uri
from config import SQLALCHEMY_MIGRATE_REPO as db_repo
from app import db
import os

db.create_all()
if not os.path.exists(db_repo):
    api.create(db_repo, 'database repository')
    api.version_control(db_uri, db_repo)
else:
    api.version_control(db_uri, db_repo, api.version(db_repo))