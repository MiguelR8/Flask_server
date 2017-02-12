# coding=utf-8
from app import app
from flask import render_template, redirect, request, flash
from .forms import ReqUploadForm, CertUploadForm
#from config import import_cryptotools
from OpenSSL.crypto import load_certificate
from datetime import datetime

import sys
import os
#allow import from cryptotools path
sys.path.insert(0, os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3]))

from cryptotools import getX509FromReq, getCommonName, getCryptoExt


data = {'index':
				{'title': u'Entidad certificadora'},
		'request':
				{'title': u'Solicitar certificado'},
		'validate':
				{'title': u'Validar certificado'}
		}

def flash_errors(form):
	for field in form:
		try:
			for e in field.errors:
				flash(e)
		except AttributeError:
			pass

##URL renderers
@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', data=data['index'])

@app.route('/request', methods=['GET', 'POST'])
def req_upload():
	form= ReqUploadForm()
	if form.validate_on_submit():
		f = request.files['doc']
		
		req_name = str(len(os.listdir(app.config['REQ_UPLOAD_FOLDER']))) + '.' +  f.filename.split('.')[-1]
		reqLocation = os.path.join(app.config['REQ_UPLOAD_FOLDER'], req_name)
		f.save(reqLocation)
		#create certificate object from request
		cert_name = str(len(os.listdir(app.config['CERT_UPLOAD_FOLDER']))) + '.pem'
		if getX509FromReq(reqLocation,
				app.config['CERT_PATH'],
				app.config['PKEY_PATH'],
				os.path.join(app.config['CERT_UPLOAD_FOLDER'], cert_name)) is None:
			flash ('Error OpenSSL')
			render_template('request.html', data=data['request'], form=form)
		
		flash ('Su solicitud de certificado ha sido procesada', category='info')
		return redirect('/')
	flash_errors(form)
	return render_template('request.html', data=data['request'], form=form)

@app.route('/validate', methods=['GET', 'POST'])
def cert_upload():
	form= CertUploadForm()
	if form.validate_on_submit():
		f = request.files['doc']
		valid = False
		time_invalid = False
		
		try:
			cert = load_certificate(getCryptoExt(f.filename.split('.')[-1]), f.stream.read())
		except:
			flash ('Archivo no es un certificado')
			return render_template('validate.html', data=data['validate'], form=form)
		
		#validate from the certificate chain?
		if cert.get_issuer().CN == getCommonName(app.config['CERT_PATH']):
			before = cert.get_notBefore()[:14]	#chop the Z or +-HHMM characters
			before = datetime.strptime(before, '%Y%m%d%H%M%S')
			after = cert.get_notAfter()[:14]
			after = datetime.strptime(after, '%Y%m%d%H%M%S')
			now = datetime.now()
			if before < now and after > now:
				valid = True
			time_invalid = not valid
		
		if valid:
			msg = 'Certificado verificado, pertenece a ' + cert.get_subject().CN
		else:
			msg = 'Se desconfía de la procedencia del certificado'
			if time_invalid:
				msg += "\nEl certificado para {} no está en su periodo de validez".format(cert.get_subject().CN)
		flash (msg, category='info')
		return redirect('/')
	flash_errors(form)
	return render_template('validate.html', data=data['validate'], form=form)
	
