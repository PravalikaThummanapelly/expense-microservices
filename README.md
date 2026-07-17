# Expense Tracker — Microservices Architecture

A microservices-based expense tracking application built to demonstrate
service-to-service communication, JWT authentication, and API gateway
patterns — with Docker/Kubernetes deployment layered on top.

## Architecture

```
Client -> api-gateway (:8000) -> users-service (:5001)    -> users_db (MySQL)
                               -> expenses-service (:5002) -> expenses_db (MySQL)
                                        |
                                        v
                            (calls users-service internally
                             to verify user identity)
```

- **users-service** — signup, login, JWT issuance, user lookup
- **expenses-service** — JWT-protected expense CRUD, verifies users via
  a live HTTP call to users-service
- **api-gateway** — single entry point; routes `/auth/*` to users-service
  and `/expenses/*` to expenses-service

## Why microservices (not a monolith)

Each service owns its own database and can be developed, deployed, and
scaled independently. They communicate only over HTTP, never by sharing
a database — a core microservices principle.

## Local setup (per service)

Each service folder has its own `requirements.txt` and `.env.example`.
For each service:

```bash
cd <service-name>
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then edit .env with your real DB password
python app.py
```

You'll need a local MySQL server running with `users_db` and
`expenses_db` databases created.

## Tech stack

Python, Flask, Flask-SQLAlchemy, MySQL, PyJWT, bcrypt, requests

## Roadmap

- [x] users-service
- [x] expenses-service
- [x] api-gateway
- [ ] Dockerize each service
- [ ] Docker Compose for local multi-service orchestration
- [ ] GitHub Actions CI/CD pipeline
- [ ] Kubernetes deployment (Helm, Prometheus/Grafana)
