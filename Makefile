testwebserver:
	python web/core.py

runwebserver:
	cd web && gunicorn --workers 3 --bind unix:pylitwoops.sock --log-level debug --log-file logs/gunicorn.log app:app &

runscript:
	python worker/check.py

startstreaming:
	python streaming/start.py &

user-refresh:
	python scripts/lists.py refresh 763301230999404544

stream: user-refresh startstreaming

heartbeat:
	python worker/heartbeat.py

test:
	nosetests tests/

dump:
	python scripts/dumpdata.py
