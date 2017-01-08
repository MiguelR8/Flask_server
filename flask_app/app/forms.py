from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length

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
	doc = FileField('PDF', validators=[FileRequired(message='El archivo es obligatorio'), FileAllowed(['pdf'], message='El archivo debe ser un PDF')])
	#certificate or something else?
	cert = FileField('certificate', validators=[FileRequired(message='El archivo es obligatorio'), FileAllowed(['p12', 'pfx'], message='El archivo debe ser del formato PKCS#12')])
	submit = SubmitField('Subir')
	
