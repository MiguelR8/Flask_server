#Credit to https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
import imp

try:
	from migrate.versioning import api
except ImportError:
	from config import activate_venv
	activate_venv()
	from migrate.versioning import api

from app import db
from config import SQLALCHEMY_DATABASE_URI as db_uri
from config import SQLALCHEMY_MIGRATE_REPO as db_repo
v = api.db_version(db_uri, db_repo)
migration = db_repo + ('/versions/%03d_migration.py' % (v+1))
tmp_module = imp.new_module('old_model')
old_model = api.create_model(db_uri, db_repo)
exec(old_model, tmp_module.__dict__)
script = api.make_update_script_for_model(db_uri, db_repo, tmp_module.meta, db.metadata)
open(migration, "wt").write(script)
api.upgrade(db_uri, db_repo)
v = api.db_version(db_uri, db_repo)
print('New migration saved as ' + migration)
print('Current database version: ' + str(v))