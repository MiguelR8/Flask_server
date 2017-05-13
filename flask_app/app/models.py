from app import db

class Author(db.Model):
	id		 = db.Column(db.Integer, primary_key = True)
	name	 = db.Column(db.String(50), nullable = False, unique = True)

class User(db.Model):
	id		 = db.Column(db.ForeignKey('author.id'), primary_key = True)
	name	 = db.Column(db.ForeignKey('author.name'))
	password = db.Column(db.String(80), nullable = False)					#for now, the sha512 (actual size depends on len(cryptotools.hash_object(...)))
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
		return str(self.id)
	#can the user have several certificates? 
	
#User to Group relation
class Membership(db.Model):
	id	   = db.Column(db.Integer, primary_key = True)
	group  = db.Column(db.ForeignKey('group.id'))
	member = db.Column(db.ForeignKey('user.id'))
	
class Group(db.Model):
	id		 = db.Column(db.ForeignKey('author.id'), primary_key = True)
	name	 = db.Column(db.ForeignKey('author.name'))
	#admin   = db.Column(db.ForeignKey('user.id'))				#no admins for group schemes, yet

class SignedDoc(db.Model):
	id      = db.Column(db.Integer, primary_key = True)
	name    = db.Column(db.String(50))
	author  = db.Column(db.ForeignKey('author.id'))
	is_user = db.Column(db.Boolean, nullable = False)			#so a mask will be used
	digest  = db.Column(db.String(80), nullable = False)		#SHA512 hash (actual size depends on len(cryptotools.hash_object(...)))
	signed_digest = db.Column(db.String(320), nullable = False)	#hash's signature	(actual size depends on len(cryptotools.encrypt_hash_object(...)))