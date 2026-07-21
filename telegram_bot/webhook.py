import asyncio
import logging
import threading
from concurrent.futures import TimeoutError as FutureTimeoutError

from aiogram import Bot, Dispatcher
from aiogram.types import Update

from admin import router as admin_router
from booking import router as booking_router
from config import TOKEN
from database import create_db
from main import configure_bot, router as main_router


logger = logging.getLogger(__name__)

dispatcher = Dispatcher()
dispatcher.include_router(admin_router)
dispatcher.include_router(booking_router)
dispatcher.include_router(main_router)

_loop = asyncio.new_event_loop()
_thread = threading.Thread(
    target=_loop.run_forever,
    name="telegram-webhook-loop",
    daemon=True,
)
_start_lock = threading.Lock()
_bot = None
_ready = False


def _ensure_loop() -> None:
    if _thread.is_alive():
        return

    with _start_lock:
        if not _thread.is_alive():
            _thread.start()


async def _ensure_bot() -> Bot:
    global _bot, _ready

    if _bot is None:
        _bot = Bot(token=TOKEN)

    if not _ready:
        create_db()
        await configure_bot(_bot)
        _ready = True
        logger.info("Telegram webhook bot is ready")

    return _bot


async def _handle_update(payload: dict) -> None:
    bot = await _ensure_bot()
    update = Update.model_validate(payload, context={"bot": bot})
    await dispatcher.feed_update(bot, update)


def process_update(payload: dict, timeout: int = 25) -> None:
    _ensure_loop()
    future = asyncio.run_coroutine_threadsafe(_handle_update(payload), _loop)

    try:
        future.result(timeout=timeout)
    except FutureTimeoutError:
        future.cancel()
        raise TimeoutError("Telegram update processing timed out") from None
