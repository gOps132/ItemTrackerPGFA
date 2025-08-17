import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Let sqlalchemy knows the models when creating tables
from app.model import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/mydb")

# echo true will log all sql statements
engine = create_async_engine(DATABASE_URL, echo=True)

# Configure the asynchronous sessionmaker
# autocommit=False and autoflush=False are standard for session management
# expire_on_commit=False prevents objects from expiring after commit, which can be useful
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# get asynchronous database session
async def get_db():
    """
    Provides asynchronous database session to API endpoints
    The 'async with' statement ensures its properly closed
    """
    async with AsyncSessionLocal() as session:
        yield session

async def create_db_and_tables():
    """
    Creates database tables based on sql alchemy models if they don't already
    exists. This should be called during application startup
    """
    async with engine.begin() as conn:
        # run async to execute synchrous DDL operations like create all
        # on the async connection
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created/ensured")