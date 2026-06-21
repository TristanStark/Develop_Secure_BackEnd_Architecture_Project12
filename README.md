# Epic Events CRM

Secure internal CRM built with **Python 3**, **Django**, **Django REST Framework**, and **PostgreSQL**.

- Django Admin as the management front end.
- PostgreSQL configured through environment variables in `epic_events/settings.py`.
- Django ORM models for clients, contract statuses, contracts, and events.
- Secure REST API endpoints for CRUD operations.
- Role-based access control for Management, Sales, and Support users.
- Search and filtering on client, contract, and event endpoints.

## Domain model

```text
User
 ├── owns many Clients as sales_contact
 ├── owns many Contracts as sales_contact
 └── supports many Events as support_contact

Client
 ├── has many Contracts
 └── has many Events

ContractStatus
 └── has many Contracts

Contract
 ├── belongs to one Client
 └── has many Events

Event
 ├── belongs to one Client
 ├── belongs to one Contract
 └── may be assigned to one Support user
```

## API endpoints

| Endpoint | Description |
| --- | --- |
| `/api/clients/` | CRUD for clients. |
| `/api/contracts/` | CRUD for contracts. |
| `/api/events/` | CRUD for events. |
| `/api/token/` | Obtain JWT access and refresh tokens. |
| `/api/token/refresh/` | Refresh a JWT token. |
| `/admin/` | Django Admin front end. |

## Role model

The project uses three role names:

- `Management Team`: staff/admin users. They can access all CRM resources.
- `Sales Team`: can create clients, update their assigned clients, view/update contracts for their assigned clients, and create events for their contracts.
- `Support Team`: can view/update events assigned to them and view clients linked to those events.

Create the groups and assign their model permissions with:

```bash
python manage.py migrate
python manage.py bootstrap_roles
```

## Local setup with uv

```bash
uv sync
cp .env.example .env
python manage.py migrate
python manage.py bootstrap_roles
python manage.py createsuperuser
python manage.py runserver
```

## Run tests

The default configuration targets PostgreSQL. A SQLite-only test settings module is included for fast local checks:

```bash
python manage.py test --settings=epic_events.test_settings
```

## Environment variables

The application is configured by environment variables. The defaults target a local PostgreSQL database named `epic_events`.

```bash
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=epic_events
POSTGRES_USER=epic_events
POSTGRES_PASSWORD=epic_events
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

For a quick smoke test without PostgreSQL, set:

```bash
DJANGO_DB_ENGINE=django.db.backends.sqlite3
```

PostgreSQL remains the expected production database and the default setting.

## Useful examples

Obtain a token:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin-password"}'
```

Filter clients by email:

```bash
curl http://127.0.0.1:8000/api/clients/?email=client@example.com \
  -H "Authorization: Bearer <access-token>"
```

Search contracts by client name:

```bash
curl http://127.0.0.1:8000/api/contracts/?client_name=Dupont \
  -H "Authorization: Bearer <access-token>"
```
