import os

os.environ.setdefault("DATABASE_URL", "postgresql://newsuser:newspass@localhost:5432/newsdb")

import pytest
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]


def postgres_available() -> bool:
    try:
        engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 2})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


POSTGRES_AVAILABLE = postgres_available()


@pytest.fixture(scope="session")
def _app():
    # Importing app.main is what actually connects to Postgres (CREATE EXTENSION,
    # create_all), so it's deferred to here rather than done at module import time.
    # Only tests that request `client`/`db_session` (and are therefore already
    # gated by `requires_postgres`) trigger this.
    from app.main import app

    return app


@pytest.fixture()
def db_session(_app):
    from sqlalchemy.orm import sessionmaker

    from app.database import engine

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE articles, stories RESTART IDENTITY CASCADE"))
        conn.commit()

    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client(_app, db_session):
    from fastapi.testclient import TestClient

    from app.database import get_db

    def override_get_db():
        db = db_session()
        try:
            yield db
        finally:
            db.close()

    _app.dependency_overrides[get_db] = override_get_db
    yield TestClient(_app)
    _app.dependency_overrides.clear()
