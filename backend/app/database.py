import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
load_dotenv()

# Use PostgreSQL when DATABASE_URL is provided.
# Otherwise, use SQLite for local development.

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./procureflow.db"
)

# Configure PostgreSQL to use Psycopg 3.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

engine_options = {
    "pool_pre_ping": True,
}

# SQLite-specific configuration.
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {
        "check_same_thread": False
    }

engine = create_engine(
    DATABASE_URL,
    **engine_options
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
