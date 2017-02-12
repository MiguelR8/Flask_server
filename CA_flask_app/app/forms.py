from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField

class ReqUploadForm(FlaskForm):
	doc    = FileField('Req', validators=[FileRequired(message='El archivo es obligatorio'), FileAllowed(['der', 'pem'], message='El archivo debe ser DER o PEM')])
	submit = SubmitField('Enviar')

class CertUploadForm(FlaskForm):
	doc    = FileField('Cert', validators=[FileRequired(message='El archivo es obligatorio'), FileAllowed(['der', 'pem'], message='El archivo debe ser DER o PEM')])
	submit = SubmitField('Enviar')
	
