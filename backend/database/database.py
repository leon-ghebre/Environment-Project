"""
database.py

Sets up the database connection for the water quality monitoring backend

This file creates:
- the database engine (connects Python to the SQLite database)
- the session factory (used to read/write data)
- the Base class (used when creating tables in models.py)

Persona coverage:
    - Lebo Xhosa: Supports quick access to the latest water safety readings
    - Jack Wilshere: Supports storing historical data for trend analysis
    - George Weah: Supports reviewing alerts and site activity over time
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL

# creates the databse engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30})

# creates the session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# the base class which all database tables will inherit from this
Base = declarative_base()
