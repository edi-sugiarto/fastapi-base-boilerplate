# FastAPI Boilerplate

A flexible and modern FastAPI boilerplate with support for both relational (SQLite, PostgreSQL) and non-relational (MongoDB) databases.

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-009688.svg?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-6.0-47A248.svg?style=flat&logo=mongodb&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-20.10+-2496ED.svg?style=flat&logo=docker&logoColor=white)

## Features

- **Flexible Database Abstraction Layer**: Seamlessly switch between SQLite, PostgreSQL and MongoDB
- **Repository Pattern**: Consistent data access across different database types
- **Environment-Based Configuration**: Easy configuration via `.env` files
- **Docker Support**: Ready-to-use Docker and docker-compose setup
- **API Documentation**: Automatic Swagger/OpenAPI documentation
- **Modular Structure**: Well-organized project structure for scalability
- **Type Hints**: Full type annotation support for better IDE integration

## Project Structure

```
fastapi-base-boilerplate/
├── app/
│   ├── api/
│   │   ├── endpoints/      # API route handlers
│   │   └── routes.py       # API route registration
│   ├── core/               # Core application components
│   ├── db/                 # Database abstraction layer
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Repository pattern implementations
│   ├── schemas/            # Pydantic schemas
│   └── services/           # Business logic layer
├── config/                 # Configuration management
├── data/                   # Data storage (SQLite, MongoDB)
├── tests/                  # Test suite
├── .env.example            # Example environment variables
├── build.sh                # Setup automation script
├── docker-compose.yaml     # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── manage.py               # Application management script
└── pyproject.toml          # Project dependencies
```

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended for fast dependency installation)
- Docker and Docker Compose (for containerized setup)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-base-boilerplate.git
   cd fastapi-base-boilerplate
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies using uv:
   ```bash
   # Install uv if you don't have it
   # pip install uv
   
   # Install dependencies from pyproject.toml
   uv pip install -e .
   ```

4. Create your environment file:
   ```bash
   cp .env.example .env
   ```

5. Run the application:
   ```bash
   python manage.py
   ```

6. Access the API documentation at http://127.0.0.1:8002/docs

### Docker Setup

1. Run the automated setup script:
   ```bash
   ./build.sh
   ```

2. Start the containers:
   ```bash
   docker-compose up -d
   ```

3. Access the API documentation at http://localhost:8002/docs

## Database Configuration

The boilerplate supports both SQLAlchemy (for relational databases) and MongoDB (for non-relational databases).

### Configuring the Database Type

In your `.env` file, set the `DATABASE_TYPE` variable:

```
# Options: "sqlalchemy", "mongodb"
DATABASE_TYPE=sqlalchemy  # or mongodb
```

### SQLAlchemy Configuration (PostgreSQL, SQLite)

```
# SQLite
SQLALCHEMY_DATABASE_URL=sqlite+aiosqlite:///data/app.db

# PostgreSQL
SQLALCHEMY_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/dbname
```

### MongoDB Configuration

```
MONGODB_URL=mongodb://admin:password@mongodb:27017/
MONGODB_DATABASE_NAME=app_db
```

## Using the Repository Pattern

The boilerplate implements the repository pattern to provide a consistent interface for data access regardless of the underlying database.

```python
# Example: Using a repository with dependency injection
from app.repositories.task_repository import TaskRepository
from app.database.db import DatabaseClient

async def get_tasks(db_client: DatabaseClient):
    repo = TaskRepository(db_client)
    tasks = await repo.get_many(limit=100)  # Get up to 100 tasks
    return tasks
```

## API Endpoints

The API follows RESTful conventions:

- `POST /api/tasks` - Create a new task
- `GET /api/tasks` - List all tasks
- `GET /api/tasks/{id}` - Get a specific task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.