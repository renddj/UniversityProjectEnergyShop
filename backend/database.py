import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL базы данных берётся из переменной окружения (Railway её задаёт автоматически)
# Для локальной разработки можно задать в файле .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/energyshop")

# Railway иногда даёт URL начинающийся с postgres://, SQLAlchemy требует postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

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
