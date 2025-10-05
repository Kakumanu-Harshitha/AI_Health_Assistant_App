import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- User Table Model ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

# --- Database Initialization ---
def create_db_and_tables():
    """Create database tables if they don’t exist."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ SQL tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"❌ ERROR: Could not create SQL tables. Error: {e}")

# --- Dependency for FastAPI ---
def get_db():
    """Dependency to provide a SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()