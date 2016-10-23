#!flask/bin/python
import ssl
context = ('cert/servercert.pem', 'cert/serverkey.pem')
from app import app
app.run(port=5000, ssl_context=context, debug=True)
