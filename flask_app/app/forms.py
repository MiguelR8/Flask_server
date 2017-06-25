from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Length, required
from app import models

_mandatory = required('Campo obligatorio')
_file_mandatory = FileRequired(message='El archivo es obligatorio')
_signschemes = [(1, 'RSA'), (2, 'Boyen')]

class RegisterForm(FlaskForm):
	username = StringField('username', validators=[_mandatory, Length(max=30, min=3, message='Nombre debe tener entre 3 y 30 caracteres')])
	password = PasswordField('password', validators=[_mandatory, Length(min=8, message='Clave debe tener al menos 8 caracteres')])
	cert	 = FileField('certificate', validators=[_file_mandatory, FileAllowed(['der', 'pem'], message='El archivo debe ser DER o PEM')])
	submit   = SubmitField('Enviar')

class LoginForm(FlaskForm):
	username	= StringField('username', validators=[_mandatory, Length(max=30, min=3, message='Nombre debe tener entre 3 y 30 caracteres')])
	signtype = SelectField('signature_type', choices = _signschemes, default=1, coerce=int, validators=[_mandatory])
	answer	= TextAreaField('challenge_answer', validators=[_mandatory])
	remember_me = BooleanField('remember_me', default=False)
	submit		= SubmitField('Enviar')

class PDFUploadForm(FlaskForm):
	doc      = FileField('PDF', validators=[_file_mandatory, FileAllowed(['pdf'], message='El archivo debe ser un PDF')])
	signtype = SelectField('signature_type', choices = _signschemes, default=1, coerce=int, validators=[_mandatory])
	group_name  = StringField('username')
	public_keys = TextAreaField('group public keys')
	digest   = TextAreaField('signed hash', validators=[_mandatory])
	submit   = SubmitField('Subir')
	
class NewGroupForm(FlaskForm):
	name    = StringField('name', validators=[_mandatory, Length(max=50, min=3, message='Nombre debe tener entre 3 y 50 caracteres')])
	master_key = TextAreaField('master group key', validators=[_mandatory])
	public_keys = TextAreaField('group public keys', validators=[_mandatory])
	answer = TextAreaField('challenge_answer', validators=[_mandatory])
	submit = SubmitField('Crear grupo')

class DocSearchForm(FlaskForm):
	doc    = FileField('PDF', validators=[_file_mandatory, FileAllowed(['pdf'], message='El archivo debe ser un PDF')])
	submit = SubmitField('Buscar por documento')

class UserSearchForm(FlaskForm):
	#delay query until database is created
	class AuthorIter:
		def __iter__(self):
			return [(u.id, u.name) for u in models.Author.query.all()].__iter__()
	
	user = SelectField('user', choices = AuthorIter(), coerce=int, validators=[_mandatory])
	submit = SubmitField('Buscar por autor')