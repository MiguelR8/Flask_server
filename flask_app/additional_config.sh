u=`stat -c %U config.py`
python -c "import os; print 'STORAGE_ROOT = \'$1\''" > config.py.tmp
cat config.py | grep -vP ^STORAGE_ROOT >> config.py.tmp;
mv config.py.tmp config.py;
chown $u config.py