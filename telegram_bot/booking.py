import logging
import re
from datetime import date, datetime, timedelta

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID, BOT_TIMEZONE, CLUB_NAME
from database import create_booking_if_available, get_user, user_exists
from keyboards import (
    confirm_keyboard,
    date_keyboard,
    duration_keyboard,
    hall_keyboard,
    places_keyboard,
    register_keyboard,
    retry_booking_keyboard,
    start_time_keyboard,
)
from settings import (
    BOOKING_DAYS,
    BOOKING_DURATIONS,
    COMMON_PC,
    FIRST_BOOKING_HOUR,
    LAST_BOOKING_HOUR,
    VIP_PC,
)


router = Router(name="booking")
logger = logging.getLogger(__name__)


def format_date(value: str) -> str:
    return date.fromisoformat(value).strftime("%d.%m.%Y")


def valid_place(place: str) -> bool:
    match = re.fullmatch(r"(PC|VIP)-(\d{2})", place)
    if not match:
        return False
    number = int(match.group(2))
    limit = COMMON_PC if match.group(1) == "PC" else VIP_PC
    return 1 <= number <= limit


def valid_date(value: str) -> bool:
    try:
        selected = date.fromisoformat(value)
    except ValueError:
        return False
    today = datetime.now(BOT_TIMEZONE).date()
    return today <= selected < today + timedelta(days=BOOKING_DAYS)


def valid_time(value: str, hours: int) -> bool:
    try:
        parsed = datetime.strptime(value, "%H:%M")
    except ValueError:
        return False
    return (
        parsed.minute == 0
        and FIRST_BOOKING_HOUR <= parsed.hour
        and parsed.hour + hours <= LAST_BOOKING_HOUR + 1
    )


async def show_booking_start(target: Message, user_id: int) -> None:
    if not user_exists(user_id):
        await target.answer(
            "Сначала зарегистрируйтесь — это займёт меньше минуты.",
            reply_markup=register_keyboard,
        )
        return

    await target.answer(
        "🎮 Бронирование компьютера\n\nВыберите зал:",
        reply_markup=hall_keyboard,
    )


@router.message(F.text == "🎮 Забронировать ПК")
async def booking_start_message(message: Message) -> None:
    await show_booking_start(message, message.from_user.id)


@router.callback_query(F.data == "booking_start")
async def booking_start_callback(callback: CallbackQuery) -> None:
    if not user_exists(callback.from_user.id):
        await callback.message.answer(
            "Сначала зарегистрируйтесь — это займёт меньше минуты.",
            reply_markup=register_keyboard,
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "🎮 Бронирование компьютера\n\nВыберите зал:",
        reply_markup=hall_keyboard,
    )
    await callback.answer()


@router.callback_query(F.data == "booking_cancel")
async def booking_cancel(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Бронирование отменено. Вы можете начать заново из главного меню."
    )
    await callback.answer("Отменено")


@router.callback_query(F.data == "hall_common")
async def hall_common(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🖥 Выберите компьютер в общем зале:",
        reply_markup=places_keyboard("common"),
    )
    await callback.answer()


@router.callback_query(F.data == "hall_vip")
async def hall_vip(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "👑 Выберите компьютер в VIP-зале:",
        reply_markup=places_keyboard("vip"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("place_"))
async def select_place(callback: CallbackQuery) -> None:
    place = callback.data.removeprefix("place_")
    if not valid_place(place):
        await callback.answer("Некорректное место", show_alert=True)
        return

    await callback.message.edit_text(
        f"🎮 {place}\n\nВыберите продолжительность:",
        reply_markup=duration_keyboard(place),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("duration_"))
async def select_duration(callback: CallbackQuery) -> None:
    try:
        _, place, hours_raw = callback.data.split("_", 2)
        hours = int(hours_raw)
    except (ValueError, AttributeError):
        await callback.answer("Не удалось прочитать выбор", show_alert=True)
        return

    if not valid_place(place) or hours not in BOOKING_DURATIONS:
        await callback.answer("Некорректный выбор", show_alert=True)
        return

    await callback.message.edit_text(
        f"🎮 {place}\n⏳ {hours} ч.\n\nВыберите дату:",
        reply_markup=date_keyboard(place, hours),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("date_"))
async def select_date(callback: CallbackQuery) -> None:
    try:
        _, place, hours_raw, booking_date = callback.data.split("_", 3)
        hours = int(hours_raw)
    except (ValueError, AttributeError):
        await callback.answer("Не удалось прочитать дату", show_alert=True)
        return

    if (
        not valid_place(place)
        or hours not in BOOKING_DURATIONS
        or not valid_date(booking_date)
    ):
        await callback.answer("Дата больше недоступна", show_alert=True)
        return

    await callback.message.edit_text(
        f"🎮 {place}\n⏳ {hours} ч.\n📅 {format_date(booking_date)}"
        "\n\nВыберите время начала:",
        reply_markup=start_time_keyboard(place, hours, booking_date),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("start_"))
async def select_start_time(callback: CallbackQuery) -> None:
    try:
        _, place, hours_raw, booking_date, start_time = callback.data.split("_", 4)
        hours = int(hours_raw)
    except (ValueError, AttributeError):
        await callback.answer("Не удалось прочитать время", show_alert=True)
        return

    if (
        not valid_place(place)
        or hours not in BOOKING_DURATIONS
        or not valid_date(booking_date)
        or not valid_time(start_time, hours)
    ):
        await callback.answer("Время больше недоступно", show_alert=True)
        return

    await callback.message.edit_text(
        "✅ Проверьте бронь:\n\n"
        f"🖥 Место: {place}\n"
        f"⏳ Продолжительность: {hours} ч.\n"
        f"📅 Дата: {format_date(booking_date)}\n"
        f"🕒 Начало: {start_time}\n\n"
        "Подтвердить?",
        reply_markup=confirm_keyboard(place, hours, booking_date, start_time),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_"))
async def confirm_booking(callback: CallbackQuery) -> None:
    try:
        _, place, hours_raw, booking_date, start_time = callback.data.split("_", 4)
        hours = int(hours_raw)
    except (ValueError, AttributeError):
        await callback.answer("Не удалось подтвердить бронь", show_alert=True)
        return

    if (
        not valid_place(place)
        or hours not in BOOKING_DURATIONS
        or not valid_date(booking_date)
        or not valid_time(start_time, hours)
    ):
        await callback.answer("Параметры брони устарели", show_alert=True)
        return

    user = get_user(callback.from_user.id)
    if user is None:
        await callback.message.answer(
            "Регистрация не найдена. Пожалуйста, зарегистрируйтесь заново.",
            reply_markup=register_keyboard,
        )
        await callback.answer()
        return

    booking_id = create_booking_if_available(
        callback.from_user.id,
        user["name"],
        place,
        hours,
        booking_date,
        start_time,
    )

    if booking_id is None:
        await callback.message.edit_text(
            "❌ Это время уже пересекается с другой бронью.\n\n"
            "Выберите другой компьютер или время.",
            reply_markup=retry_booking_keyboard(),
        )
        await callback.answer("Слот занят", show_alert=True)
        return

    display_date = format_date(booking_date)
    await callback.message.edit_text(
        "🎉 Бронь создана!\n\n"
        f"Номер брони: #{booking_id}\n"
        f"🖥 Место: {place}\n"
        f"⏳ Продолжительность: {hours} ч.\n"
        f"📅 Дата: {display_date}\n"
        f"🕒 Начало: {start_time}\n\n"
        f"Спасибо, что выбрали {CLUB_NAME}!"
    )

    try:
        await callback.bot.send_message(
            ADMIN_ID,
            "🔔 Новая бронь\n\n"
            f"Номер: #{booking_id}\n"
            f"Клиент: {user['name']}\n"
            f"Телефон: {user['phone']}\n"
            f"Место: {place}\n"
            f"Продолжительность: {hours} ч.\n"
            f"Дата: {display_date}\n"
            f"Начало: {start_time}\n"
            f"Telegram ID: {callback.from_user.id}",
        )
    except TelegramAPIError:
        logger.exception("Failed to notify admin about booking %s", booking_id)

    await callback.answer("Бронь подтверждена")
