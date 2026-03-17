import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL базы данных берётся из переменной окружения (Railway её задаёт автоматически)
# Для локальной разработки можно задать в файле .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/energyshop")

# Приводим URL к нужному формату
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Функция-зависимость для FastAPI — открывает сессию БД на время запроса
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
