"""Безопасная настройка Telegram webhook из переменных окружения.

Обязательные переменные:
- TOKEN — токен бота от BotFather
- TELEGRAM_WEBHOOK_SECRET — секрет webhook
- PUBLIC_BASE_URL — публичный адрес Render, например https://mad-alex09.onrender.com
"""

import json
import os
import sys
from urllib.parse import urlencode
from urllib.request import urlopen

WEBHOOK_PATH = "/telegram/webhook"


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name}")
    return value


def telegram_call(token: str, method: str, params: dict | None = None) -> dict:
    query = f"?{urlencode(params)}" if params else ""
    url = f"https://api.telegram.org/bot{token}/{method}{query}"
    with urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    try:
        token = required("TOKEN")
        secret = required("TELEGRAM_WEBHOOK_SECRET")
        base_url = required("PUBLIC_BASE_URL").rstrip("/")
        webhook_url = f"{base_url}{WEBHOOK_PATH}"

        result = telegram_call(
            token,
            "setWebhook",
            {
                "url": webhook_url,
                "secret_token": secret,
                "allowed_updates": json.dumps(["message", "callback_query"]),
                "drop_pending_updates": "false",
            },
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result.get("ok"):
            return 1

        info = telegram_call(token, "getWebhookInfo")
        safe_result = info.get("result", {})
        print("\nПроверка webhook:")
        print(json.dumps(safe_result, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
