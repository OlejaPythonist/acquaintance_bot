from aiogram import (  # type: ignore
    Bot,
    Dispatcher,
    executor,
)
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tgbot.middlewares.antiflood import ThrottlingMiddleware
from tgbot.handlers.user import register_user
from tgbot.database.base import Base
import logging
import asyncio
import os


def create_bot() -> tuple[Bot, Dispatcher]:
    storage = MemoryStorage()
    bot = Bot(os.environ["BOT_TOKEN"])
    dp = Dispatcher(bot, storage=storage)
    return bot, dp


async def create_db() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(
        "postgresql+asyncpg://"
        f"{os.environ['USER']}:{os.environ['PASSWD']}@"
        f"{os.environ['HOST']}/{os.environ['DATABASE_NAME']}"
    )
    session = async_sessionmaker(bind=engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return session


async def main() -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    bot, dp = create_bot()
    session = await create_db()
    register_user(dp, session)
    dp.middleware.setup(ThrottlingMiddleware())
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()   


def cli():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")


if __name__ == '__main__':
    cli()
