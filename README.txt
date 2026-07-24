MAD_ALEX — сайт и Telegram-бот в одном Render Web Service

Публичный webhook:
https://mad-alex09.onrender.com/telegram/webhook

Переменные Render Environment:
- TOKEN — токен Telegram-бота от BotFather
- ADMIN_ID — числовой Telegram ID администратора
- TELEGRAM_WEBHOOK_SECRET — секрет webhook (это НЕ токен бота)
- PUBLIC_BASE_URL — https://mad-alex09.onrender.com
- DATABASE_URL — строка подключения Neon/PostgreSQL

Проверка после деплоя:
1. Открой https://mad-alex09.onrender.com/healthz
2. telegram_configured и telegram_loaded должны быть true.
3. Открой https://mad-alex09.onrender.com/telegram/webhook — должен вернуться JSON со status=ok.

Настройка webhook без ручной сборки длинной ссылки:
PowerShell:
  $env:TOKEN="ТОКЕН_БОТА"
  $env:TELEGRAM_WEBHOOK_SECRET="СЕКРЕТ_WEBHOOK"
  $env:PUBLIC_BASE_URL="https://mad-alex09.onrender.com"
  python set_webhook.py

Важно:
- TOKEN = токен бота от BotFather.
- TELEGRAM_WEBHOOK_SECRET = отдельный секрет webhook.
- Не отправляй эти значения в чат и не добавляй их в Git.

Для совместимости приложение также принимает старые пути /webhook и /telegram-webhook,
но канонический путь остаётся /telegram/webhook.
