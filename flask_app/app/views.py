# coding=utf-8
from app import app, db, lm
from app import models
from flask import render_template, redirect, request, flash, send_file
from .forms import *
from flask_login import login_user, logout_user, current_user, login_required
import os

import sys
#allow import from cryptotools path
sys.path.insert(0, os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3]))
from cryptotools import getCommonName, verify_hash_with_certificate, hash_object, verify_boyen

def signed_documents_to_json(uid=None):
	results = []
	if uid is None:
		for a in models.Author.query.all():
			docs = []
			for d in models.SignedDoc.query.filter_by(author = a.id).all():
				docs.append({'name': d.name, 'hash':d.digest, 'sig':d.signed_digest})
			if len(docs) > 0:
				results.append({'name': a.name, 'documents':docs})
	else:
		a = models.Author.query.filter_by(id = uid).first()
		if a is not None:
			docs = []
			for d in models.SignedDoc.query.filter_by(author = uid).all():
				docs.append({'name': d.name, 'hash':d.digest, 'sig':d.signed_digest})		
			if len(docs) > 0:
				results.append({'name': a.name, 'documents':docs})
		
	return results

#wrap in a function to delay loading until really needed
def data_for(key):
	return {'/index.html':
                {'title': u'Documentos firmados',
                'data': signed_documents_to_json()},
        '/login.html':
                {'title': u'Iniciar sesión'},
        '/doc_upload.html':
                {'title': u'Subir archivo'},
        '/register.html':
				{'title': u'Crear cuenta'},
		'/register_group.html':
				{'title': u'Crear grupo', 'challenge' : 'Cifre este texto para verificar que es miembro del grupo'}
        }[key]

def flash_errors(form):
	for field in form:
		try:
			for e in field.errors:
				flash(e)
		except AttributeError:
			pass

def redirect_if_logged_in(url):
	if current_user is not None:
		redirect(url)
		
@lm.user_loader
def load_user(id):
	return models.User.query.get(int(id))

##URL renderers

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	userform = UserSearchForm()
	docform = DocSearchForm()
	
	kwargs = {}
	kwargs['data'] = data_for('/index.html')
	kwargs['uform'] = userform
	kwargs['dform'] = docform
	
	if userform.validate_on_submit() or docform.validate_on_submit():
		if userform.validate_on_submit():
			#fetch all documents from user
			res = signed_documents_to_json(userform.user.data)
		else:
			#fetch user
			res = ""
			doc = request.files['doc']
			pdfLocation = os.path.join(app.config['DOCUMENT_UPLOAD_FOLDER'],
				'___' + os.path.basename(doc.filename))
			doc.save(pdfLocation)
			digest = hash_object(pdfLocation, isFile = True)
			os.remove(pdfLocation)
			
			d = models.SignedDoc.query.filter_by(digest = digest).first()
			if d is not None:
				u = models.User.query.get(d.author)
				if u is not None:
					res = u.name
		#filter documents to display
		kwargs['data']['data'] = res
	else:
		flash_errors(userform)
		flash_errors(docform)
	if current_user.is_authenticated:
		#Documents signed by user
		kwargs['user_docs'] = signed_documents_to_json(current_user.id)
		#And signed by a member of the group the user belongs to
		#gdocs = 
	return render_template('index.html', **kwargs)

@app.route('/login', methods=['GET', 'POST'])
def login():
	redirect_if_logged_in('/')
	form = LoginForm()
	if form.validate_on_submit():
		h = hash_object(form.password.data)
		user = models.User.query.filter_by(name = form.username.data, password = h).first()
		if user is None:
			flash(u'Usuario o contraseña incorrectos')
		else:
			login_user(user, remember = form.remember_me.data)
			return redirect('/index')
	flash_errors(form)
	return render_template('login.html', data=data_for('/login.html'), form=form)
	
@app.route('/logout')
def logout():
	logout_user()
	return redirect('/')
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	redirect_if_logged_in('/')
	form = RegisterForm()
	if form.validate_on_submit():
		if models.Author.query.filter_by(name = form.username.data).first():
			flash('Nombre ya registrado')
		else:
			h = hash_object(form.password.data)
			ext = '.' + request.files['cert'].filename.split('.')[-1]
			cert = os.path.join(app.config['USER_CERTIFICATE_FOLDER'],
					form.username.data + ext)
			request.files['cert'].save(cert)
			#TODO: validate chain of trust
			try:
				if getCommonName(cert) == form.username.data:
					#Save as author
					author = models.Author(name = form.username.data)
					db.session.add(author)
					db.session.commit()
					
					#Save as user (author info needed)
					author = models.Author.query.filter_by(name = form.username.data).first()
					user = models.User(id = author.id, name = author.name, password = h)
					db.session.add(user)
					db.session.commit()
					return redirect('/')
				else:
					flash('Certificado no pertenece al usuario')
			except ValueError:
				flash('Archivo no es un certificado')
			#remove on failure
			os.remove(cert)
	flash_errors(form)
	return render_template('register.html', data=data_for('/register.html'),
			form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_main():
	form = PDFUploadForm()
	if form.validate_on_submit():
		
		doc = request.files['doc']
		#TODO: clean up
		signed = form.digest.data
		signtype = form.signtype.data
		
		pdfLocation = os.path.join(app.config['DOCUMENT_UPLOAD_FOLDER'],
			os.path.basename(doc.filename))
		filename = os.path.basename(doc.filename)
		doc.save(pdfLocation)
		digest = hash_object(pdfLocation, isFile = True)
		
		#Verify file hasn't been uploaded yet (trusting collision freedom of SHA512)
		if models.SignedDoc.query.filter_by(digest = digest).first() is not None:
			flash('Archivo ya existe')
		else:
			if signtype == 1:		#RSA
				try:
					verify_hash_with_certificate(digest,
						signed,
						os.path.join(app.config['USER_CERTIFICATE_FOLDER'],
							current_user.name + '.pem'))
					db.session.add(models.SignedDoc(name = filename,
						author = current_user.id,
						is_user = True,
						digest = digest,
						signed_digest = signed))
					db.session.commit()
					
					return redirect('/')
				except Exception:
					flash('Error de validación: el documento y/o certificado no corresponden con la firma')
			elif signtype == 2:		#Boyen
				group_name = form.group_name.data
				g = models.Group.query.filter_by(name = group_name).first()
				if g is None:
					flash('Grupo no registrado, debe crearse antes de subir documentos')
				else:
					public_keys = form.public_keys.data.strip()
					if len(public_keys) == 0:		#load saved keys instead
						with open(os.path.join(app.config['GROUP_KEYS_FOLDER'], str(g.id) + '.pkeys')) as f:
							public_keys = f.read()
					
					with open(os.path.join(app.config['GROUP_KEYS_FOLDER'], str(g.id) + '.mkey')) as f:
						master_key = f.read()
					
					if verify_boyen(master_key, public_keys, digest, signed):
						db.session.add(models.SignedDoc(name = filename,
							author = g.id,
							is_user = False,
							digest = digest,
							signed_digest = signed))
						db.session.commit()
						return redirect('/')
					else:
						flash('Fallo de validación, verifique que las claves y la firma son correctas')
			else:
				flash('Tipo de firma incorrecto, elija otro')
		os.remove(pdfLocation)
	flash_errors(form)
	return render_template('doc_upload.html', data=data_for('/doc_upload.html'), form=form)
	
@app.route('/register_group', methods=['GET', 'POST'])
@login_required
def create_group():
	form = NewGroupForm()
	if form.validate_on_submit():
		group_name = form.name.data
		master_key = form.master_key.data
		public_keys = form.public_keys.data
		challenge = form.answer.data
		if models.Group.query.filter_by(name = group_name).first() is None:
			#validate challenge
			if (verify_boyen(master_key, public_keys,
					data_for('/register_group.html')['challenge'],
					challenge)):
				
				##add group
				
				#as author
				db.session.add(models.Author(name = group_name))
				db.session.commit()
				
				#as group
				gid = models.Author.query.filter_by(name = group_name).first().id
				db.session.add(models.Group(id = gid, name = group_name))
				db.session.commit()
				
				#save keys
				gid = str(gid)
				with open(os.path.join(app.config['GROUP_KEYS_FOLDER'],
						gid + '.mkey'), 'w') as f:
					f.write(master_key)
				with open(os.path.join(app.config['GROUP_KEYS_FOLDER'],
						gid + '.pkeys'), 'w') as f:
					f.write(public_keys)
				
				return redirect('/')
			else:
				flash('Fallo de validación, verifique que las claves y la firma son correctas')
		else:
			flash(u'Grupo ya existe con ese nombre')
	else:
		flash_errors(form)
	return render_template('register_group.html', data=data_for('/register_group.html'), form=form)

       
@app.route('/files/<file>')
@login_required
def download_file(filename):
	path = os.path.join(app.config['DOCUMENT_UPLOAD_FOLDER'], filename)
	return send_file(path, as_attachment = True)