"""
data_loader.py

Provides the database session factory for all routes and services.
Replaces the original pandas CSV loading approach with SQLAlchemy sessions.

Persona coverage:
    - All personas: every endpoint depends on database access
    - Jack Wilshere: SQLAlchemy indexed queries are faster than
      pandas filtering 200k+ rows in memory for trend analysis
    - George Weah: faster query responses under time pressure
      during contamination events
    - Lebo Xhosa: reliable data access underpins every safety decision
"""

from database.database import SessionLocal


def get_db():
    """Provides a database session and ensures it is closed after use.

    Yields:
        Session: A SQLAlchemy session object for querying the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
