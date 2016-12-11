#context = ('cert/servercert.pem', 'cert/serverkey.pem')
from app import app
if __name__ == '__main__':
	app.run(port=5000, debug=True)#, ssl_context=context)
