# 📋 Application Tracker API

A production-ready REST API for tracking job applications built with **FastAPI**, **PostgreSQL**, **Redis**, and **Celery**.

🔗 **Live API:** https://application-tracker-api-o7rq.onrender.com/
📄 **Interactive Docs:** https://application-tracker-api-o7rq.onrender.com/docs

---

## ✨ Features

- 🔐 **JWT Authentication** — register, login, protected routes
- 👤 **User Management** — update profile, delete account
- 📝 **Application Tracking** — create and manage job applications with soft delete
- 🔄 **Status Transitions** — enforced workflow with applied, interviewing, offer, accepted, rejected, and ghosted states
- 📊 **Dashboard Analytics** — response rate, offer rate, acceptance rate, average days to response
- 📈 **Monthly Trends** — track application volume month by month
- ⏰ **Reminders** — set reminders per application with Celery task scheduling
- 🔔 **Notifications** — in-app notification system
- 🛡️ **Admin Panel** — admin role, user management, audit logs
- 📋 **Audit Logs** — every action tracked automatically
- ⚡ **Redis Caching** — dashboard stats cached for performance
- 🚦 **Rate Limiting** — login endpoint protected against brute force
- 🗄️ **Alembic Migrations** — full database migration history
- ✅ **Full Test Suite** — all tests run against real PostgreSQL
- 📝 **Request Correlation IDs** — trace individual requests across application logs 
- 📋 **Centralized Logging** — structured application and HTTP request logging 
- 🚨 **Global Exception Handling** — centralized handling of unexpected application errors 
- 🗂️ **Database Indexing** — B-tree indexes for frequently queried fields 
- 🐳 **Dockerized Development** — reproducible local application environment 
- 🔄 **CI Pipeline** — automated testing, linting, and Docker build validation

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Programming language |
| FastAPI | Web framework |
| SQLAlchemy | ORM / Database layer |
| PostgreSQL | Production database |
| Alembic | Database migrations |
| Redis | Caching + Celery broker |
| Celery | Background task queue |
| JWT (python-jose) | Authentication |
| Passlib + Bcrypt | Password hashing |
| SlowAPI | Rate limiting |
| Pytest | Testing |

---

## ☁️ Deployment The API is deployed on Render and uses a production PostgreSQL database and Redis/Key Value instance. ### Production Architecture
text
                         ┌─────────────────┐
                         │     Client      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Render Web     │
                         │    Service      │
                         │    FastAPI      │
                         └───────┬─┬───────┘
                                 │ │
                    ┌────────────┘ └────────────┐
                    ▼                           ▼
             ┌──────────────┐          ┌────────────────┐
             │  PostgreSQL  │          │ Redis / Key    │
             │   Database   │          │     Value      │
             └──────────────┘          └───────┬────────┘
                                               │
                                  ┌────────────┴────────────┐
                                  ▼                         ▼
                           ┌─────────────┐          ┌──────────────┐
                           │   Celery    │          │ APScheduler  │
                           │   Worker    │          │  Scheduler   │
                           └─────────────┘          └──────────────┘
                                       └──────────────┘ 

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/lakshay-gahlawat/application-tracker-api.git
cd application-tracker-api
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Windows:

```powershell
copy .env.example .env
```

Mac/Linux:

```bash
cp .env.example .env
```

Edit `.env` and fill in your values.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the complete local stack

```bash
docker compose up --build
```

The Docker Compose stack includes:

- FastAPI application
- Redis
- Celery worker
- APScheduler

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Alternative: Run services individually

Start Redis on:

```text
localhost:6379
```

Start Celery worker:

```bash
celery -A app.core.celery_app.celery_app worker --loglevel=info
```

Start scheduler:

```bash
python run_scheduler.py
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

---

## ⚙️ Environment Variables

Create a `.env` file based on `.env.example`:

```env
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

DATABASE_URL=postgresql://user:password@localhost/app_tracker
TEST_DATABASE_URL=postgresql://user:password@localhost/app_tracker_test

REDIS_URL=redis://localhost:6379/0

REMINDER_CHECK_INTERVAL=10
REMINDER_PROCESSING_TIMEOUT_MINUTES=5

RESEND_API_KEY=your_resend_api_key

TESTING=False
```

Never commit real secrets, database credentials, or API keys to the repository.

---

## 📡 API Endpoints

### Auth & Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | ❌ | Register new user |
| POST | `/api/v1/auth/login` | ❌ | Login and get JWT token (rate limited) |
| GET | `/api/v1/users/me` | ✅ | Get current user profile |
| PUT | `/api/v1/users/me` | ✅ | Update profile |
| DELETE | `/api/v1/users/me` | ✅ | Delete account |

### Applications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/applications/` | ✅ | Create application |
| GET | `/api/v1/applications/` | ✅ | List applications (paginated, filterable) |
| GET | `/api/v1/applications/{id}` | ✅ | Get application |
| PUT | `/api/v1/applications/{id}` | ✅ | Update application |
| DELETE | `/api/v1/applications/{id}` | ✅ | Soft delete application |
| PATCH | `/api/v1/applications/{id}/status` | ✅ | Update status (enforced transitions) |

### Status Transition Rules

```text
applied → interviewing, rejected, ghosted
interviewing → offer, rejected, ghosted
offer → accepted, rejected
ghosted → interviewing
accepted → final
rejected → final
```

### Reminders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/reminders/` | ✅ | Create reminder for an application |
| GET | `/api/v1/reminders/` | ✅ | Get all reminders |
| GET | `/api/v1/reminders/today` | ✅ | Get today's reminders |
| PATCH | `/api/v1/reminders/{id}/complete` | ✅ | Mark reminder as done |

### Dashboard

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/dashboard/stats` | ✅ | Full stats (cached in Redis) |
| GET | `/api/v1/dashboard/monthly-trends` | ✅ | Monthly application volume |

### Notifications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/notifications/` | ✅ | Get all notifications |
| PATCH | `/api/v1/notifications/{id}/read` | ✅ | Mark as read |

### Admin

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/admin/me` | 👑 Admin | Verify admin access |
| GET | `/api/v1/admin/users` | 👑 Admin | List all users |
| GET | `/api/v1/admin/audit-logs` | 👑 Admin | View all audit logs |

---

## 📁 Project Structure

```text
application-tracker-api/
├── alembic/
│   └── versions/             # Database migrations
├── app/
│   ├── core/                 # Config, auth, Redis, Celery, rate limiter
│   ├── database/             # Database session setup
│   ├── dependencies/         # JWT auth, DB dependencies
│   ├── models/               # SQLAlchemy models
│   ├── router/               # API route handlers
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/             # Business logic layer
│   ├── tasks/                # Celery background tasks
│   └── main.py               # App entry point
├── tests/
│   ├── factories/            # Test data factories
│   ├── utils/                # Test helpers
│   ├── conftest.py           # Fixtures and setup
│   ├── test_auth.py
│   ├── test_application.py
│   ├── test_reminders.py
│   ├── test_dashboard.py
│   ├── test_admin.py
│   ├── test_notification.py
│   ├── test_reminder_service.py
│   └── test_reminder_tasks.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🧪 Running Tests

Tests run against a real PostgreSQL test database.

```bash
pytest tests/ -v
```

---

## 🔍 Linting

Run Ruff:

```bash
ruff check .
```

---

## 🐳 Docker

Build the application:

```bash
docker compose build
```

Start the complete local stack:

```bash
docker compose up
```

Stop the stack:

```bash
docker compose down
```

The Docker Compose stack includes:

- FastAPI application
- Redis
- Celery worker
- APScheduler

---

## 🔄 CI

GitHub Actions automatically validates the project through:

- Automated tests
- Ruff linting
- Docker build validation

---

## 📌 Project Status

**Version: 1.0.0**

The project has been deployed as a production-oriented backend API and demonstrates practical backend engineering concepts including:

- Authentication and authorization
- Database design and migrations
- PostgreSQL indexing
- Redis caching
- Celery background task processing
- APScheduler-based scheduling
- Rate limiting
- Audit logging
- Structured logging
- Request correlation IDs
- Global exception handling
- Automated testing
- Dockerization
- CI/CD validation
- Cloud deployment

The current free Render deployment intentionally does not continuously host the Celery worker and APScheduler processes.

---

## 📬 Contact

Lakshay Gahlawat