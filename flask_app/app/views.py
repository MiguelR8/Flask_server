# coding=utf-8
from app import app, db, models
from flask import render_template, redirect, request, flash
from .forms import LoginForm, PDFUploadForm, RegisterForm
import os
from cryptotools import getCommonName
from hashlib import sha512
from sqlalchemy import func

data = {'/index.html':
                {'title': u'Grupos',
                'data':[
                        {'name':'GroupA', 'documents':[
                                {'hash':0x123456, 'sig':'xq1wd8vm4kt'},
                                {'hash':0x1e9c3a, 'sig':'fk93j+ds.df'}
                        ], 'pkey': 'alsjkvn234'},
                        {'name':'GroupB', 'documents':[
                                {'hash':0x14c6b9, 'sig':'klcfjsgkihs'},
                                {'hash':0x5b0733, 'sig':'csedf#zs=(g'}
                        ], 'pkey': 'oopwcksjf5'}
                ]},
        '/login.html':
                {'title': u'Iniciar sesión'},
        '/doc_upload.html':
                {'title': u'Subir archivo'},
        '/register.html':
				{'title': u'Crear cuenta'}
        }

def flash_errors(form):
	for field in form:
		try:
			for e in field.errors:
				flash(e)
		except AttributeError:
			pass

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', data=data['/index.html'])

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		h = sha512(form.password.data).digest().decode('utf_16')	#to Unicode
		if db.session.query(models.User).filter_by(name = unicode(form.username.data), password = h).first() is None:
			flash(u'Usuario o contraseña incorrectos')
		else:
			#do login
			return redirect('/index')
	flash_errors(form)
	return render_template('login.html', data=data['/login.html'], form=form)
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		if db.session.query(models.User).filter_by(name = form.username.data).first():
			flash('Usuario ya existe')
		else:
			h = sha512(form.password.data).digest().decode('utf_16')
			user = models.User(name = unicode(form.username.data), password = h)
			ext = '.' + request.files['cert'].filename.split('.')[-1]
			cert = os.path.join(app.config['USER_CERTIFICATE_FOLDER'], form.username.data + ext)
			request.files['cert'].save(cert)
			#TODO: validate chain of trust
			try:
				if getCommonName(cert) == form.username.data:
					db.session.add(user)
					db.session.commit()
					return redirect('/index')
				else:
					flash('Certificado no pertenece al usuario')
			except ValueError:
				flash('Archivo no es un certificado')
			#remove on failure
			#os.remove(cert)
	flash_errors(form)
	return render_template('register.html', data=data['/register.html'], form=form)


@app.route('/upload', methods=['GET', 'POST'])
def upload_main():
	form= PDFUploadForm()
	if form.validate_on_submit():
		#verify certificate belongs to logged user
		f = request.files['doc']
		
		pdfLocation = os.path.join(app.config['DOCUMENT_UPLOAD_FOLDER'], f.filename + '.nsig')
		#save non-signed and signed in different locations in case signing doesn't support simultaneous read-write
		signedPdfLocation = os.path.join(app.config['DOCUMENT_UPLOAD_FOLDER'], f.filename)
		
		f.save(pdfLocation)
		#sign with request.files['cert']
		#title = ' '.join(f.filename.split('.')[:-1] or f.filename)
		#author = get group name
		#confFile = app.config['PDF_SIGN_CONF_FILE']
		#mypdfsigner.add_metadata_sign(pdfLocation, signedPdfLocation, '', '', '', False, False, True, title, author, '', '', confFile)
		#os.remove(pdfLocation)
		return redirect('/index')
	flash_errors(form)
	return render_template('doc_upload.html', data=data['/doc_upload.html'], form=form)
