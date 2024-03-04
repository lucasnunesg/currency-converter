from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def get_session():
    """Yields a session to perform database operations."""
    with Session(engine) as session:
        yield session
