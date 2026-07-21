import os
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


TOKEN = required_env("TOKEN")

try:
    ADMIN_ID = int(required_env("ADMIN_ID"))
except ValueError as error:
    raise RuntimeError("ADMIN_ID must be an integer") from error

DATA_DIR = Path(
    os.getenv("DATA_DIR", Path(__file__).resolve().parent / "data")
).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "game_club_bot.db"
CLUB_NAME = os.getenv("CLUB_NAME", "Game Club").strip() or "Game Club"
CLUB_ADDRESS = os.getenv("CLUB_ADDRESS", "Адрес уточняется").strip()
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@admin").strip()

try:
    BOT_TIMEZONE = ZoneInfo(os.getenv("BOT_TIMEZONE", "Asia/Qyzylorda"))
except ZoneInfoNotFoundError:
    BOT_TIMEZONE = ZoneInfo("UTC")
