# 📋 Application Tracker API

A production-ready REST API for tracking job applications built with **FastAPI**, **PostgreSQL**, **Redis**, and **Celery**.

🔗 **Live API:** _coming soon_
📄 **Interactive Docs:** `/api/v1/docs`

---

## ✨ Features

- 🔐 **JWT Authentication** — register, login, protected routes
- 👤 **User Management** — update profile, delete account
- 📝 **Application Tracking** — create and manage job applications with soft delete
- 🔄 **Status Transitions** — enforced workflow (applied → interviewing → offer → accepted)
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

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/lakshay-gahlawat/application-tracker-api.git
cd application-tracker-api

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux
# Edit .env and fill in your values

# 5. Run database migrations
alembic upgrade head

# 6. Start Redis (required for caching and reminders)
# Make sure Redis is running on localhost:6379

# 7. Start Celery worker (for reminders)
celery -A app.core.celery_app worker --loglevel=info

# 8. Run the server
uvicorn app.main:app --reload

# 9. Open docs
# http://127.0.0.1:8000/api/v1/docs
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
```

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
```
applied → interviewing, rejected, ghosted
interviewing → offer, rejected, ghosted
offer → accepted, rejected
ghosted → interviewing
accepted → (final)
rejected → (final)
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

```
application-tracker-api/
├── alembic/                  # Database migrations
│   └── versions/
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

Tests run against a real PostgreSQL test database — no mocking of DB layer.

```bash
pytest tests/ -v
```

---

## 📬 Contact

**Lakshay Gahlawat**

[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:lakshaygahlawat65@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/lakshay-gahlawat)
