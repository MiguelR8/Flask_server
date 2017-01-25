u=`stat -c %U config.py`
python -c "import os; print 'STORAGE_ROOT = \'$1\''" > config.py.tmp
cat config.py | grep -vP ^STORAGE_ROOT >> config.py.tmp;
mv config.py.tmp config.py;
chown $u config.py

#this doesn't fit in the Makefile style because it only concerns file existence and not data change
if [ ! -e $1/app.db ];
then
	su -c "python db_create.py" $2;
fi