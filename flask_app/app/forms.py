from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField, TextAreaField
from wtforms.validators import InputRequired, Length, required
from app import models

class RegisterForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(message='Nombre de usuario obligatorio'), Length(max=30, min=3, message='Nombre debe tener entre 3 y 30 caracteres')])
	password = PasswordField('password', validators=[InputRequired(message='Clave obligatoria'), Length(min=8, message='Clave debe tener al menos 8 caracteres')])
	cert	 = FileField('certificate', validators=[FileRequired(message='Certificado obligatorio'), FileAllowed(['der', 'pem'], message='El archivo debe ser DER o PEM')])
	submit   = SubmitField('Enviar')

class LoginForm(FlaskForm):
	username	= StringField('username', validators=[InputRequired(message='Nombre de usuario obligatorio'), Length(max=30, min=3, message='Nombre debe tener entre 3 y 30 caracteres')])
	password	= PasswordField('password', validators=[InputRequired(message='Clave obligatoria')])
	remember_me = BooleanField('remember_me', default=False)
	submit		= SubmitField('Enviar')

class PDFUploadForm(FlaskForm):
	doc    = FileField('PDF', validators=[FileRequired(message='El archivo es obligatorio'), FileAllowed(['pdf'], message='El archivo debe ser un PDF')])
	digest = TextAreaField('signed hash', validators=[required('Campo obligatorio')])
	submit = SubmitField('Subir')
	
class NewGroupForm(FlaskForm):
	name    = StringField('name', validators=[InputRequired(message='Nombre obligatorio'), Length(max=50, min=3, message='Nombre debe tener entre 3 y 50 caracteres')])
	master_key = TextAreaField('master group key', validators=[required('Campo obligatorio')])
	public_keys = TextAreaField('group public keys', validators=[required('Campo obligatorio')])
	challenge = TextAreaField('challenge', validators=[required('Campo obligatorio')])
	submit = SubmitField('Crear grupo')
	
