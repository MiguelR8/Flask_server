from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length

class LoginForm(FlaskForm):
	username = StringField('username', validators=[Required(), Length(max=30, min=3, message='Nombre debe tener entre 3 y 30 caracteres')])
	password = PasswordField('password', validators=[Required()])
	remember_me = BooleanField('remember_me', default=False)
	submit = SubmitField('submit')
