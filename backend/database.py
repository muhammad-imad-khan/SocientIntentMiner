from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import get_settings

settings = get_settings()

# Railway provides postgresql://, SQLAlchemy async needs postgresql+asyncpg://
_db_url = settings.DATABASE_URL
if _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    from sqlalchemy import text

    async with engine.begin() as conn:
        # Create enum types if they don't exist (avoids conflict on restart)
        for enum_name, values in [
            ("plantier", "'free','pro','enterprise'"),
            ("leadstatus", "'new','contacted','qualified','converted','dismissed'"),
        ]:
            await conn.execute(text(
                f"DO $$ BEGIN CREATE TYPE {enum_name} AS ENUM ({values}); EXCEPTION WHEN duplicate_object THEN NULL; END $$"
            ))
        await conn.run_sync(Base.metadata.create_all)
