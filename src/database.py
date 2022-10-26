from contextlib import asynccontextmanager
from sqlalchemy.ext import asyncio as sa_asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from settings import settings

engine = sa_asyncio.create_async_engine(
    settings.pg.dns, pool_recycle=settings.pg.pool_recycle
)
Session = sessionmaker(
    bind=engine,
    class_=sa_asyncio.AsyncSession,
    expire_on_commit=False
)
metadata = MetaData(schema=settings.pg.pg_schema)
Base = declarative_base(metadata=metadata)


@asynccontextmanager
async def session_scope():
    async_session = Session()
    try:
        yield async_session
        await async_session.commit()
    except Exception:
        await async_session.rollback()
        raise
    finally:
        await async_session.close()
