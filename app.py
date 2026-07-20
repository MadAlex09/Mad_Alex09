from flask import Flask, render_template, request, jsonify
import os
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "requests.db"


def create_database():
    """Создаёт базу данных и таблицу заявок, если их ещё нет."""

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
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

    connection.commit()
    connection.close()


def save_request(name, contact, service, budget, message):
    """Сохраняет новую заявку в базу данных."""

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO requests (name,
                              contact,
                              service,
                              budget,
                              message,
                              created_at)
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

    connection.commit()
    connection.close()


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
            return jsonify(
                {
                    "success": False,
                    "message": "Не удалось получить данные формы.",
                }
            ), 400

        name = str(data.get("name", "")).strip()
        contact = str(data.get("contact", "")).strip()
        service = str(data.get("service", "")).strip()
        budget = str(data.get("budget", "")).strip()
        message = str(data.get("message", "")).strip()

        if len(name) < 2:
            return jsonify(
                {
                    "success": False,
                    "message": "Введите ваше имя.",
                }
            ), 400

        if len(contact) < 3:
            return jsonify(
                {
                    "success": False,
                    "message": "Введите Telegram, телефон или электронную почту.",
                }
            ), 400

        if len(message) < 5:
            return jsonify(
                {
                    "success": False,
                    "message": "Расскажите немного подробнее о вашем проекте.",
                }
            ), 400

        save_request(
            name=name,
            contact=contact,
            service=service,
            budget=budget,
            message=message,
        )

        print("=" * 60)
        print("НОВАЯ ЗАЯВКА С САЙТА")
        print(f"Имя: {name}")
        print(f"Контакт: {contact}")
        print(f"Услуга: {service}")
        print(f"Бюджет: {budget}")
        print(f"Сообщение: {message}")
        print("=" * 60)

        return jsonify(
            {
                "success": True,
                "message": "Заявка успешно отправлена! Я свяжусь с вами в ближайшее время.",
            }
        )

    except Exception as error:
        print(f"Ошибка при сохранении заявки: {error}")

        return jsonify(
            {
                "success": False,
                "message": "Произошла ошибка. Попробуйте отправить заявку ещё раз.",
            }
        ), 500


@app.errorhandler(404)
def page_not_found(error):
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify(
        {
            "success": False,
            "message": "Внутренняя ошибка сервера.",
        }
    ), 500


create_database()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
