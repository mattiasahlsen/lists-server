run-dev:
	FLASK_APP=server.py FLASK_ENV=development flask run --host=0.0.0.0 --port=5000

run:
	FLASK_APP=server.py FLASK_ENV=production flask run --host=0.0.0.0
