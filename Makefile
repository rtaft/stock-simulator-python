
all: cleanall venv gendb

cleanall: cleanenv clean

clean:
	for file in `find . -name "*.py[co]" -print -o -name "*~" -print -o -name ".#*" -print`; do echo $$file; rm $$file; done
	rm database/database.py
cleanenv:
	rm -Rf 

venv: venv/bin/activate
venv/bin/activate:
	test -d venv || virtualenv -p /usr/bin/python3 venv

gendb: venv
	sqlacodegen mysql+mysqlconnector://traderjoe:stockman@localhost/stocks > database/database.py