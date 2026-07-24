import hmac
import os
from pathlib import Path
import sys

from flask import Flask, jsonify, render_template, request

from storage import create_database, save_request

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.jinja_env.auto_reload = True

BASE_DIR = Path(__file__).resolve().parent
BOT_DIR = BASE_DIR / "telegram_bot"
WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "").strip()
BOT_ENABLED = all(
    os.getenv(name, "").strip()
    for name in ("TOKEN", "ADMIN_ID", "TELEGRAM_WEBHOOK_SECRET")
)

process_telegram_update = None
if BOT_ENABLED:
    sys.path.insert(0, str(BOT_DIR))
    from webhook import process_update as process_telegram_update


def error_response(message, status_code):
    """Возвращает единый JSON-ответ об ошибке."""

    return jsonify({"success": False, "message": message}), status_code


@app.route("/")
def home():
    """Главная страница сайта."""

    return render_template("index.html")


@app.route("/send-request", methods=["POST"])
def send_request():
    """Получает заявку из формы и сохраняет её в SQLite."""

    try:
        data = request.get_json(silent=True)

        if not data:
            return error_response("Не удалось получить данные формы.", 400)

        name = str(data.get("name", "")).strip()
        contact = str(data.get("contact", "")).strip()
        service = str(data.get("service", "")).strip()
        budget = str(data.get("budget", "")).strip()
        message = str(data.get("message", "")).strip()
        lang = "ru" if str(data.get("lang", "en")).lower() == "ru" else "en"

        if len(name) < 2:
            return error_response("Введите ваше имя." if lang == "ru" else "Please enter your name.", 400)

        if len(contact) < 3:
            return error_response(
                "Введите Telegram, телефон или электронную почту." if lang == "ru" else "Enter your Telegram, phone number, or email.",
                400,
            )

        if len(message) < 5:
            return error_response(
                "Расскажите немного подробнее о вашем проекте." if lang == "ru" else "Please tell me a little more about your project.",
                400,
            )

        save_request(
            name=name,
            contact=contact,
            service=service,
            budget=budget,
            message=message,
        )

        return jsonify(
            {
                "success": True,
                "message": ("Заявка успешно отправлена! Я свяжусь с вами в ближайшее время." if lang == "ru" else "Your request has been sent successfully! I will contact you shortly."),
            }
        )

    except Exception:
        app.logger.exception("Не удалось сохранить заявку")
        return error_response(
            "Произошла ошибка. Попробуйте отправить заявку ещё раз." if locals().get("lang") == "ru" else "An error occurred. Please try sending the request again.",
            500,
        )


@app.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    """Принимает защищённые обновления Telegram Bot API."""

    if not BOT_ENABLED or process_telegram_update is None:
        return error_response("Telegram-бот пока не настроен.", 503)

    supplied_secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token",
        "",
    )
    if not hmac.compare_digest(supplied_secret, WEBHOOK_SECRET):
        return error_response("Доступ запрещён.", 403)

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "update_id" not in data:
        return error_response("Некорректное обновление Telegram.", 400)

    try:
        process_telegram_update(data)
    except Exception:
        app.logger.exception("Не удалось обработать обновление Telegram")
        return error_response("Не удалось обработать обновление.", 500)

    return "", 204


@app.route("/healthz")
def healthcheck():
    return jsonify({"status": "ok", "telegram": BOT_ENABLED})


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_server_error(_error):
    return error_response("Внутренняя ошибка сервера.", 500)


create_database()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
