from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./tickets.db"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30} # Добавь timeout
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base создаем ТУТ, чтобы models.py мог его забрать
Base = declarative_base()

# Функция для получения сессии (удобно для эндпоинтов)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()