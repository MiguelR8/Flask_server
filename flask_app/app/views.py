from app import app
from flask import render_template, redirect
from .forms import LoginForm

data = {'/index.html':
                {'title':'Groups',
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
                {'title':'Log in'}
        }

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', data=data['/index.html'])

@app.route('/login', methods=['GET', 'POST'])
def aside():
	form = LoginForm()
	if form.validate_on_submit():
		return redirect('/index')
	return render_template('login.html', data=data['/login.html'], form=form)
