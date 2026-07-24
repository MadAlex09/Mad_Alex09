import logging
import re
from datetime import date, datetime, timedelta
from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Message
from config import ADMIN_ID, BOT_TIMEZONE, CLUB_NAME
from database import create_booking_if_available, get_user, get_user_language, user_exists
from keyboards import confirm_keyboard, date_keyboard, duration_keyboard, hall_keyboard, places_keyboard, register_keyboard, retry_booking_keyboard, start_time_keyboard
from settings import BOOKING_DAYS, BOOKING_DURATIONS, COMMON_PC, FIRST_BOOKING_HOUR, LAST_BOOKING_HOUR, VIP_PC
from translations import hour_word, t

router = Router(name="booking"); logger = logging.getLogger(__name__)
def language(user_id): return get_user_language(user_id)
def format_date(value): return date.fromisoformat(value).strftime("%d.%m.%Y")
def valid_place(place):
    match = re.fullmatch(r"(PC|VIP)-(\d{2})", place)
    if not match: return False
    return 1 <= int(match.group(2)) <= (COMMON_PC if match.group(1) == "PC" else VIP_PC)
def valid_date(value):
    try: selected = date.fromisoformat(value)
    except ValueError: return False
    today = datetime.now(BOT_TIMEZONE).date(); return today <= selected < today + timedelta(days=BOOKING_DAYS)
def valid_time(value, hours):
    try: parsed = datetime.strptime(value, "%H:%M")
    except ValueError: return False
    return parsed.minute == 0 and FIRST_BOOKING_HOUR <= parsed.hour and parsed.hour + hours <= LAST_BOOKING_HOUR + 1

async def show_booking_start(target: Message, user_id: int):
    lang = language(user_id)
    if not user_exists(user_id): await target.answer(t(lang, "register_first"), reply_markup=register_keyboard(lang)); return
    await target.answer(t(lang, "booking_title"), reply_markup=hall_keyboard(lang))

@router.message(F.text.in_({"🎮 Book a PC", "🎮 Забронировать ПК"}))
async def booking_start_message(message): await show_booking_start(message, message.from_user.id)

@router.callback_query(F.data == "booking_start")
async def booking_start_callback(callback):
    lang = language(callback.from_user.id)
    if not user_exists(callback.from_user.id): await callback.message.answer(t(lang, "register_first"), reply_markup=register_keyboard(lang)); await callback.answer(); return
    await callback.message.edit_text(t(lang, "booking_title"), reply_markup=hall_keyboard(lang)); await callback.answer()

@router.callback_query(F.data == "booking_cancel")
async def booking_cancel(callback):
    lang = language(callback.from_user.id); await callback.message.edit_text(t(lang, "booking_cancelled")); await callback.answer(t(lang, "cancel_alert"))

@router.callback_query(F.data == "hall_common")
async def hall_common(callback):
    lang = language(callback.from_user.id); await callback.message.edit_text(t(lang, "choose_common_pc"), reply_markup=places_keyboard("common", lang)); await callback.answer()

@router.callback_query(F.data == "hall_vip")
async def hall_vip(callback):
    lang = language(callback.from_user.id); await callback.message.edit_text(t(lang, "choose_vip_pc"), reply_markup=places_keyboard("vip", lang)); await callback.answer()

@router.callback_query(F.data.startswith("place_"))
async def select_place(callback):
    lang = language(callback.from_user.id); place = callback.data.removeprefix("place_")
    if not valid_place(place): await callback.answer(t(lang, "invalid_place"), show_alert=True); return
    await callback.message.edit_text(t(lang, "choose_duration", place=place), reply_markup=duration_keyboard(place, lang)); await callback.answer()

@router.callback_query(F.data.startswith("duration_"))
async def select_duration(callback):
    lang = language(callback.from_user.id)
    try: _, place, raw = callback.data.split("_", 2); hours = int(raw)
    except (ValueError, AttributeError): await callback.answer(t(lang, "read_choice_error"), show_alert=True); return
    if not valid_place(place) or hours not in BOOKING_DURATIONS: await callback.answer(t(lang, "invalid_choice"), show_alert=True); return
    await callback.message.edit_text(t(lang, "choose_date", place=place, hours=hours, hour_word=hour_word(lang, hours)), reply_markup=date_keyboard(place, hours, lang)); await callback.answer()

@router.callback_query(F.data.startswith("date_"))
async def select_date(callback):
    lang = language(callback.from_user.id)
    try: _, place, raw, booking_date = callback.data.split("_", 3); hours = int(raw)
    except (ValueError, AttributeError): await callback.answer(t(lang, "read_date_error"), show_alert=True); return
    if not valid_place(place) or hours not in BOOKING_DURATIONS or not valid_date(booking_date): await callback.answer(t(lang, "date_unavailable"), show_alert=True); return
    await callback.message.edit_text(t(lang, "choose_time", place=place, hours=hours, hour_word=hour_word(lang, hours), date=format_date(booking_date)), reply_markup=start_time_keyboard(place, hours, booking_date, lang)); await callback.answer()

@router.callback_query(F.data.startswith("start_"))
async def select_start_time(callback):
    lang = language(callback.from_user.id)
    try: _, place, raw, booking_date, start_time = callback.data.split("_", 4); hours = int(raw)
    except (ValueError, AttributeError): await callback.answer(t(lang, "read_time_error"), show_alert=True); return
    if not valid_place(place) or hours not in BOOKING_DURATIONS or not valid_date(booking_date) or not valid_time(start_time, hours): await callback.answer(t(lang, "time_unavailable"), show_alert=True); return
    await callback.message.edit_text(t(lang, "review_booking", place=place, hours=hours, hour_word=hour_word(lang, hours), date=format_date(booking_date), time=start_time), reply_markup=confirm_keyboard(place, hours, booking_date, start_time, lang)); await callback.answer()

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_booking(callback):
    lang = language(callback.from_user.id)
    try: _, place, raw, booking_date, start_time = callback.data.split("_", 4); hours = int(raw)
    except (ValueError, AttributeError): await callback.answer(t(lang, "confirm_error"), show_alert=True); return
    if not valid_place(place) or hours not in BOOKING_DURATIONS or not valid_date(booking_date) or not valid_time(start_time, hours): await callback.answer(t(lang, "booking_expired"), show_alert=True); return
    user = get_user(callback.from_user.id)
    if user is None: await callback.message.answer(t(lang, "registration_missing"), reply_markup=register_keyboard(lang)); await callback.answer(); return
    booking_id = create_booking_if_available(callback.from_user.id, user["name"], place, hours, booking_date, start_time)
    if booking_id is None: await callback.message.edit_text(t(lang, "slot_busy"), reply_markup=retry_booking_keyboard(lang)); await callback.answer(t(lang, "slot_busy_alert"), show_alert=True); return
    display = format_date(booking_date)
    await callback.message.edit_text(t(lang, "booking_created", booking_id=booking_id, place=place, hours=hours, hour_word=hour_word(lang, hours), date=display, time=start_time, club=CLUB_NAME))
    try:
        await callback.bot.send_message(ADMIN_ID, "🔔 Новая бронь\n\n" f"Номер: #{booking_id}\nКлиент: {user['name']}\nТелефон: {user['phone']}\nМесто: {place}\nПродолжительность: {hours} ч.\nДата: {display}\nНачало: {start_time}\nTelegram ID: {callback.from_user.id}")
    except TelegramAPIError: logger.exception("Failed to notify admin about booking %s", booking_id)
    await callback.answer(t(lang, "booking_confirmed"))
