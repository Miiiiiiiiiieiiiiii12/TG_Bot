import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dotenv import load_dotenv
from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не задан!")

# Убираем sslmode из ссылки, так как asyncpg его не понимает
if "?sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "")

for prefix in ("postgresql+psycopg2://", "postgresql://", "postgres://"):
    if DATABASE_URL.startswith(prefix):
        DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len(prefix):]
        break

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"ssl": "require"}, # Для Pterodactyl/внешних БД
    pool_pre_ping=True,              # Проверка соединения перед использованием (решает твою ошибку)
    pool_recycle=1800                # Пересоздание соединений раз в 30 минут
)

# Инициализируем сессии
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)