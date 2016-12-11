import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

from flask import Flask

app = Flask(__name__)
app.config.from_object('config')
from app import views

