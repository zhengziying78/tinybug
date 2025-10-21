# Models

Data models, database schemas, and data access layer for the application.

## Contents

- **mutation.py**: Shared mutation specifications consumed by mutators and
  workflows.
- **Database**: (future) SQLModel table definitions
- **Schemas**: (future) Pydantic models for API request/response validation
- **Migrations**: (future) Database migration utilities and helpers

## Tech Stack

- SQLModel (SQLAlchemy + Pydantic)
- PostgreSQL database
- Alembic for migrations
