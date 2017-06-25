. ../flask/bin/activate
pip install Flask
pip install flask-wtf
pip install flask-sqlalchemy
pip install sqlalchemy-migrate
pip install flask-login
pip install pyOpenSSL
pip install selenium
#needed for Firefox driver in selenium
curl -L https://github.com/mozilla/geckodriver/releases/download/v0.16.1/geckodriver-v0.16.1-linux64.tar.gz > geckodriver-v0.16.1-linux64.tar.gz
tar -C ../../flask/bin -zxvf geckodriver-v0.16.1-linux64.tar.gz
