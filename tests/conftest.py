import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.deps import get_db

TEST_DB_URL = "sqlite:///./test_jobs.db"

@pytest.fixture(scope="session")
def engine():
    if os.path.exists("test_jobs.db"):
        os.remove("test_jobs.db")

    eng = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, future=True)
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()

    if os.path.exists("test_jobs.db"):
        os.remove("test_jobs.db")

@pytest.fixture()
def db_session(engine):
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
