testwebserver:
	python web/core.py

runwebserver:
	cd web && gunicorn --workers 3 --bind unix:pylitwoops.sock --log-level debug --log-file logs/gunicorn.log app:app &

runscript:
	python worker/check.py

startstreaming:
	python streaming/start.py

heartbeat:
	python worker/heartbeat.py
