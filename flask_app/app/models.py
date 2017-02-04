from app import db

#User to Group relation
class Membership(db.Model):
	id	   = db.Column(db.Integer, primary_key = True)
	group  = db.Column(db.ForeignKey('group.id'))
	member = db.Column(db.ForeignKey('user.id'))

class User(db.Model):
	id		 = db.Column(db.Integer, primary_key = True)
	name	 = db.Column(db.String(50), nullable = False, unique = True)
	password = db.Column(db.String(64), nullable = False)					#for now, the sha512
	
	@property
	def is_active(self):
		return True

	@property
	def is_authenticated(self):
		return True

	@property
	def is_anonymous(self):
		return False
		
	def get_id(self):
		return unicode(self.id)
	
	#cert	 = db.Column(db.String(50), nullable = False, unique = True)	#location is USER_CERTIFICATE_FOLDER/self.name
	#can the user have several certificates? 
	
class Group(db.Model):
	id	    = db.Column(db.Integer, primary_key = True)
	name    = db.Column(db.String(50), nullable = False, unique = True)
	#admin   = db.Column(db.ForeignKey('user.id'))				#need to enforce membership to apply to admin (at controller level)

class SignedDocs(db.Model):
	id     = db.Column(db.Integer, primary_key = True)
	name   = db.Column(db.String(50))
	author = db.Column(db.Integer, db.ForeignKey('user.id'))	#for now, groups don't write documents