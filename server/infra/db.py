import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.core.config import settings  

# encode של ODBC connection string מה-.env
odbc_encoded = urllib.parse.quote_plus(settings.DB_URL)
SQLALCHEMY_URL = f"mssql+pyodbc:///?odbc_connect={odbc_encoded}"

engine = create_engine(SQLALCHEMY_URL, pool_pre_ping=True, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
