from datetime import datetime
import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.jinja_env.auto_reload = True

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "requests.db"


def create_database():
    """Создаёт базу данных и таблицу заявок, если их ещё нет."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS requests
            (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                contact    TEXT NOT NULL,
                service    TEXT,
                budget     TEXT,
                message    TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_request(name, contact, service, budget, message):
    """Сохраняет новую заявку в базу данных."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO requests (
                name,
                contact,
                service,
                budget,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                contact,
                service,
                budget,
                message,
                datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            ),
        )


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

        if len(name) < 2:
            return error_response("Введите ваше имя.", 400)

        if len(contact) < 3:
            return error_response(
                "Введите Telegram, телефон или электронную почту.",
                400,
            )

        if len(message) < 5:
            return error_response(
                "Расскажите немного подробнее о вашем проекте.",
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
                "message": "Заявка успешно отправлена! Я свяжусь с вами в ближайшее время.",
            }
        )

    except (sqlite3.Error, TypeError, ValueError):
        app.logger.exception("Не удалось сохранить заявку")
        return error_response(
            "Произошла ошибка. Попробуйте отправить заявку ещё раз.",
            500,
        )


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
