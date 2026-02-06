# 📊 Realtime Analytics Dashboard

[![CI Status](https://github.com/danilkativodar/realtime-analytics-fastapi/actions/workflows/ci.yml/badge.svg)](https://github.com/danilkativodar/realtime-analytics-fastapi/actions/workflows/ci.yml) All CI checks pass
[![Python Version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/release/python-3110/)
[![Code Coverage](https://img.shields.io/badge/coverage-70%25%2B-brightgreen)](./tests/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A high-performance backend service built with FastAPI for collecting, aggregating, and visualizing user events in real-time. This project showcases a production-ready architecture with async processing, WebSocket support, and comprehensive CI/CD automation.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Running Tests](#-running-tests)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Project Structure](#-project-structure)
- [License](#license)

---

## ✨ Features

- 🔌 **Event Ingestion**: Receive user events (clicks, page views, custom events) via REST API and WebSocket
- 📈 **Real-Time Aggregation**: Automatic metric aggregation (hourly, daily, user-based) using background workers
- 🎨 **Live Dashboard**: Interactive dashboard with WebSocket-powered live updates
- ⚡ **Fully Async Architecture**: Built on FastAPI for maximum performance and concurrency
- 🔄 **Message Queue**: Celery with RabbitMQ for reliable background job processing
- 💾 **Smart Caching**: Redis for session management and real-time statistics
- 🔐 **User Authentication**: JWT-based auth with SQLAlchemy integration
- 🛡️ **Resilience**: Health checks, error handling, and graceful degradation
- 📊 **Monitoring**: Flower dashboard for Celery task monitoring
- 🐳 **Docker-Ready**: Complete Docker Compose setup for easy local development
- ✅ **Well-Tested**: Comprehensive test suite with 70%+ code coverage and CI/CD pipeline

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | 🚀 FastAPI, Uvicorn |
| **ORM & Database** | 🗄️ SQLAlchemy (async), PostgreSQL |
| **Caching & Queues** | ⚡ Redis, RabbitMQ |
| **Background Jobs** | 📦 Celery, Flower |
| **Data Validation** | ✓ Pydantic, Pydantic-Settings |
| **WebSocket** | 🔌 websockets |
| **Testing** | 🧪 Pytest, pytest-asyncio, pytest-cov |
| **Code Quality** | 🎯 Ruff, Black, mypy |
| **Infrastructure** | 🐳 Docker, Docker Compose |
| **CI/CD** | ⚙️ GitHub Actions |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT SIDE                              │
│                   (Web/Mobile App)                           │
└────────────┬────────────────────────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
   REST API    WebSocket
      │             │
┌─────▼─────────────▼───────────────────────────────────────┐
│               FASTAPI APPLICATION                          │
│  • Event ingestion endpoints                               │
│  • Real-time WebSocket connections                         │
│  • User authentication & authorization                     │
│  • Health checks and diagnostics                           │
└─────┬──────────────────────────────────────────────────────┘
      │
      ├─────────────────────────┬────────────────────────┐
      │                         │                        │
    Redis                   RabbitMQ                PostgreSQL
 (Cache &              (Message Broker)           (Primary DB)
  Sessions)                    │                        │
                              │                        │
                    ┌──────────▼────────────┐          │
                    │  CELERY WORKERS       │          │
                    │  • Aggregation tasks  │          │
                    │  • Cleanup jobs       │          │
                    │  • Monitoring         │          │
                    └──────────┬────────────┘          │
                               │                        │
                               └────────────┬───────────┘
                                           │
                           ┌───────────────▼──────────┐
                           │   FLOWER DASHBOARD       │
                           │   (Task Monitoring)      │
                           └──────────────────────────┘
```

**Data Flow:**
1. Client sends events via REST API or WebSocket
2. FastAPI validates and persists events to PostgreSQL
3. Events are enqueued to RabbitMQ for async processing
4. Celery workers consume tasks and aggregate metrics
5. Aggregated data is cached in Redis
6. WebSocket updates notify clients in real-time

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git installed

### Installation & Running

```bash
# 1. Clone the repository
git clone https://github.com/danilkativodar/realtime-analytics-fastapi.git
cd realtime-analytics-fastapi

# 2. Create environment file from template (adjust if needed)
cp .env.example .env

# 3. Start all services with Docker Compose
# This will start: API, PostgreSQL, Redis, RabbitMQ, Celery Worker
docker-compose up -d

# 4. Run database migrations
docker-compose exec api poetry run alembic upgrade head

# 5. Access the application
# API Docs:        http://localhost:8000/docs
# ReDoc Docs:      http://localhost:8000/redoc
# Flower Monitor:  http://localhost:5555
# Health Check:    http://localhost:8000/health
```

**What's happening?**
- `docker-compose up -d` spins up all services (API, PostgreSQL, Redis, RabbitMQ)
- Services have health checks to ensure they're ready
- The API automatically connects to the database and message broker
- Celery workers start processing background jobs immediately

> ⚠️ If services fail to start, check logs with: `docker-compose logs -f api`

---

## 📚 API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, visit:

- **Swagger UI (Interactive)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc (Alternative UI)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema (JSON)**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

All endpoints are fully documented with request/response schemas, examples, and error codes.

### Key Endpoints

```
POST   /api/v1/events              Create a new event
GET    /api/v1/analytics/summary   Get aggregated metrics
GET    /api/v1/analytics/hourly    Get hourly statistics
GET    /api/v1/analytics/daily     Get daily statistics
WS     /ws/events                  WebSocket connection for live updates
POST   /auth/register              Register new user
POST   /auth/login                 Login user
GET    /health                     Health check endpoint
```

---

## ⚙️ Configuration

Configuration is managed through environment variables in `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/analytics
POSTGRES_DB=analytics
POSTGRES_USER=user
POSTGRES_PASSWORD=your_secure_password

# Redis Configuration
REDIS_URL=redis://:your_redis_password@redis:6379/0
REDIS_PASSWORD=your_redis_password

# RabbitMQ Configuration
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Application Configuration
SECRET_KEY=your_secret_key_here
SECRET=your_jwt_secret_here
ENVIRONMENT=development  # or production
DEBUG=true

# Flower Monitoring
FLOWER_USER=admin
FLOWER_PASSWORD=your_flower_password
```

See `.env.example` for a complete list of all configuration options.

---

## 🧪 Running Tests

The project uses **Pytest** for testing with async support and SQLite for isolated test environments.

### Run All Tests
```bash
# Run tests in container
docker-compose exec api poetry run pytest tests/ -v

# Or run locally (requires local environment setup)
poetry run pytest tests/ -v --cov=app --cov-report=term-missing
```

### Run Specific Test Suite
```bash
# Test API endpoints
docker-compose exec api poetry run pytest tests/test_events_api.py -v

# Test Celery tasks
docker-compose exec api poetry run pytest tests/test_celery_tasks.py -v

# Test Redis service
docker-compose exec api poetry run pytest tests/test_redis_service.py -v

# Test WebSocket functionality
docker-compose exec api poetry run pytest tests/test_websocket.py -v

# Test analytics API
docker-compose exec api poetry run pytest tests/test_analytics_api.py -v
```

### Coverage Report
```bash
# Generate detailed coverage report
docker-compose exec api poetry run pytest tests/ \
  --cov=app \
  --cov-report=html \
  --cov-report=term-missing

# View HTML report
# Open htmlcov/index.html in your browser
```

---

## 🔄 CI/CD Pipeline

The project uses **GitHub Actions** for continuous integration with the following checks:

### Quality Checks
- ✅ **Code Formatting**: Black formatter validation
- ✅ **Linting**: Ruff static analysis
- ✅ **Type Checking**: mypy strict mode

### Testing
- ✅ **Unit Tests**: Comprehensive test suite with pytest
- ✅ **Code Coverage**: Minimum 70% coverage threshold
- ✅ **Database**: Tests run against SQLite in-memory database
- ✅ **Async Support**: Full async/await test support

### Pipeline Status
[![CI Status](https://github.com/danilkativodar/realtime-analytics-fastapi/actions/workflows/ci.yml/badge.svg)](https://github.com/danilkativodar/realtime-analytics-fastapi/actions/workflows/ci.yml)

View full pipeline configuration in [.github/workflows/ci.yml](.github/workflows/ci.yml)

---

## 📁 Project Structure

```
realtime-analytics-fastapi/
├── alembic/                           # Database migrations
│   ├── versions/                      # Migration scripts
│   ├── env.py                         # Alembic environment config
│   └── script.py.mako                 # Migration template
│
├── app/                               # Main application package
│   ├── main.py                        # FastAPI app initialization
│   ├── core/                          # Core configurations
│   │   ├── config.py                  # Settings management
│   │   ├── db.py                      # Database setup
│   │   ├── auth.py                    # Authentication logic
│   │   ├── celery.py                  # Celery configuration
│   │   └── logging.py                 # Logging setup
│   │
│   ├── models/                        # SQLAlchemy ORM models
│   │   ├── event.py                   # Event model
│   │   └── user.py                    # User model
│   │
│   ├── schemas/                       # Pydantic request/response schemas
│   │   ├── event.py                   # Event DTOs
│   │   ├── analytics.py               # Analytics DTOs
│   │   ├── health.py                  # Health check DTOs
│   │   └── user.py                    # User DTOs
│   │
│   ├── api/                           # API endpoints
│   │   ├── routers.py                 # Main router configuration
│   │   └── endpoints/                 # Endpoint implementations
│   │       ├── events.py              # Event ingestion endpoints
│   │       ├── analytics.py           # Analytics query endpoints
│   │       ├── auth.py                # Authentication endpoints
│   │       ├── health.py              # Health check endpoint
│   │       ├── tasks.py               # Task management endpoints
│   │       └── websocket.py           # WebSocket endpoints
│   │
│   ├── crud/                          # Database CRUD operations
│   │   ├── event.py                   # Event CRUD
│   │   └── analytics.py               # Analytics CRUD
│   │
│   ├── services/                      # Business logic layer
│   │   ├── redis_service.py           # Redis caching
│   │   ├── websocket_manager.py       # WebSocket connection management
│   │   └── background_tasks.py        # Background task utilities
│   │
│   ├── tasks/                         # Celery background tasks
│   │   ├── aggregation_tasks.py       # Metric aggregation
│   │   ├── cleanup_tasks.py           # Data cleanup
│   │   ├── monitoring_tasks.py        # System monitoring
│   │   ├── realtime_tasks.py          # Real-time processing
│   │   └── decorators.py              # Custom Celery decorators
│   │
│   └── validators/                    # Pydantic validators
│       └── event.py                   # Event validation logic
│
├── tests/                             # Test suite
│   ├── conftest.py                    # Pytest configuration
│   ├── test_events_api.py             # Event API tests
│   ├── test_analytics_api.py          # Analytics API tests
│   ├── test_celery_tasks.py           # Celery task tests
│   ├── test_redis_service.py          # Redis service tests
│   ├── test_websocket.py              # WebSocket tests
│   └── mocks/                         # Mock objects
│       ├── event_mocks.py             # Event test fixtures
│       ├── celery_mocks.py            # Celery mocks
│       ├── redis_mocks.py             # Redis mocks
│       ├── user_mocks.py              # User fixtures
│       └── websocket_mocks.py         # WebSocket mocks
│
├── docker-compose.yml                 # Local development services
├── Dockerfile                         # Application image
├── Makefile                           # Build automation
├── pyproject.toml                     # Poetry dependencies
├── alembic.ini                        # Alembic configuration
└── README.md                          # This file
```

**Key Directories:**
- `app/core/` - Core application setup (database, auth, config)
- `app/api/endpoints/` - All route handlers
- `app/models/` - Database schema definitions
- `app/tasks/` - Celery background job definitions
- `tests/` - All test files organized by feature

---

## 🤝 Development

### Setting Up Local Environment

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install --with dev

# Activate virtual environment
poetry shell
```

### Code Quality Commands

```bash
# Format code with Black
poetry run black app/

# Sort imports with isort
poetry run isort app/

# Lint with Ruff
poetry run ruff check app/

# Type check with mypy
poetry run mypy app/

# Run all quality checks
poetry run black --check app/
poetry run ruff check app/
poetry run mypy app/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# View migration history
alembic history
```

---

## 📦 Deployment

For production deployment:

1. **Environment Variables**: Set all required `.env` variables in your deployment platform
2. **Database**: Use managed PostgreSQL service (AWS RDS, DigitalOcean, etc.)
3. **Cache**: Use managed Redis service
4. **Message Queue**: Use managed RabbitMQ or alternative
5. **Monitoring**: Configure Flower for task monitoring
6. **Logging**: Integrate with centralized logging (ELK, Datadog, etc.)

See `Dockerfile` and `docker-compose.yml` for containerization details.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Danil Tivodar**
- Email: danilkativodar@gmail.com
- GitHub: [@danilkativodar](https://github.com/danilkativodar)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Celery](https://docs.celeryproject.io/) - Distributed task queue
- [Redis](https://redis.io/) - In-memory data store
- [PostgreSQL](https://www.postgresql.org/) - Reliable relational database

---

<div align="center">

**Built with ⚡ and ❤️ using FastAPI**

</div>
