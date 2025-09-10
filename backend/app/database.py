from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ PostgreSQL URL
DATABASE_URL = "postgresql+psycopg2://muser:health369@localhost:5432/bharat_health"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
