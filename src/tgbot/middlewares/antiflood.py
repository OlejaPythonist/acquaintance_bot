import asyncio
from aiogram import Dispatcher, types  # type: ignore
from aiogram.dispatcher import DEFAULT_RATE_LIMIT  # type: ignore
from aiogram.dispatcher.handler import CancelHandler, current_handler  # type: ignore
from aiogram.dispatcher.middlewares import BaseMiddleware  # type: ignore
from aiogram.utils.exceptions import Throttled # type: ignore


class ThrottlingMiddleware(BaseMiddleware):  # type: ignore
    def __init__(
            self,
            limit: int=DEFAULT_RATE_LIMIT,
            key_prefix: str="antiflood_") -> None:
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(
            self,
            message: types.Message,
            _) -> None:
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(
                handler,
                "throttling_rate_limit",
                self.rate_limit
            )
            try:
                key = getattr(
                    handler,
                    "throttling_key",
                    f"{self.prefix}_{handler.__name__}"
                )
            except AttributeError:
                key = getattr(
                    handler,
                    "throttling_key",
                    f"{self.prefix}_{handler.func.__name__}"
                ) 
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def message_throttled(
            self,
            message: types.Message,
            throttled: Throttled) -> None:
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count <= 2:
            pass
        await asyncio.sleep(delta)
