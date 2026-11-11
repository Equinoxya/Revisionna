.PHONY: install backend frontend seed test lint docker clean

install:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
	cd frontend && npm install

seed:
	cd backend && .venv/bin/flask --app wsgi:app init-db && .venv/bin/flask --app wsgi:app seed

backend:
	cd backend && .venv/bin/flask --app wsgi:app run --port 5000

frontend:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/pytest
	cd backend && .venv/bin/python scripts/verifier_contenu.py

lint:
	cd backend && .venv/bin/ruff check .
	cd frontend && npm run lint

docker:
	docker compose up --build

clean:
	rm -rf backend/.venv backend/instance backend/*.db frontend/node_modules frontend/dist
