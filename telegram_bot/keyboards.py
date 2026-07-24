from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from config import BOT_TIMEZONE
from settings import BOOKING_DAYS, BOOKING_DURATIONS, COMMON_PC, FIRST_BOOKING_HOUR, LAST_BOOKING_HOUR, VIP_PC
from translations import hour_word, t

remove_keyboard = ReplyKeyboardRemove()

language_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="🇬🇧 English", callback_data="language_en"),
    InlineKeyboardButton(text="🇷🇺 Русский", callback_data="language_ru"),
]])


def main_menu(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t(language, "menu_book"))],
        [KeyboardButton(text=t(language, "menu_prices")), KeyboardButton(text=t(language, "menu_shop"))],
        [KeyboardButton(text=t(language, "menu_profile")), KeyboardButton(text=t(language, "menu_address"))],
        [KeyboardButton(text=t(language, "menu_support")), KeyboardButton(text=t(language, "menu_settings"))],
    ], resize_keyboard=True, input_field_placeholder=t(language, "menu_placeholder"))


def register_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t(language, "register"))]], resize_keyboard=True)


def phone_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t(language, "send_phone"), request_contact=True)],
        [KeyboardButton(text=t(language, "cancel"))],
    ], resize_keyboard=True, one_time_keyboard=True)


def hall_keyboard(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(language, "hall_common", count=COMMON_PC), callback_data="hall_common")],
        [InlineKeyboardButton(text=t(language, "hall_vip", count=VIP_PC), callback_data="hall_vip")],
        [InlineKeyboardButton(text=t(language, "cancel_inline"), callback_data="booking_cancel")],
    ])


def places_keyboard(kind: str, language: str) -> InlineKeyboardMarkup:
    prefix, count, icon = ("PC", COMMON_PC, "🖥") if kind == "common" else ("VIP", VIP_PC, "👑")
    rows, row = [], []
    for number in range(1, count + 1):
        place = f"{prefix}-{number:02d}"
        row.append(InlineKeyboardButton(text=f"{icon} {place}", callback_data=f"place_{place}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text=t(language, "back_halls"), callback_data="booking_start")])
    rows.append([InlineKeyboardButton(text=t(language, "cancel_inline"), callback_data="booking_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def duration_keyboard(place: str, language: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"⏳ {hours} {hour_word(language, hours)}", callback_data=f"duration_{place}_{hours}")] for hours in BOOKING_DURATIONS]
    rows.append([InlineKeyboardButton(text=t(language, "restart"), callback_data="booking_start")])
    rows.append([InlineKeyboardButton(text=t(language, "cancel_inline"), callback_data="booking_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def date_keyboard(place: str, hours: int, language: str) -> InlineKeyboardMarkup:
    today = datetime.now(BOT_TIMEZONE).date(); rows, row = [], []
    for offset in range(BOOKING_DAYS):
        selected = today + timedelta(days=offset)
        label = t(language, "today") if offset == 0 else t(language, "tomorrow") if offset == 1 else selected.strftime("%d.%m")
        row.append(InlineKeyboardButton(text=f"📅 {label}", callback_data=f"date_{place}_{hours}_{selected.isoformat()}"))
        if len(row) == 2: rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text=t(language, "restart"), callback_data="booking_start")])
    rows.append([InlineKeyboardButton(text=t(language, "cancel_inline"), callback_data="booking_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def start_time_keyboard(place: str, hours: int, booking_date: str, language: str) -> InlineKeyboardMarkup:
    last_start = LAST_BOOKING_HOUR - hours + 1; rows, row = [], []
    for hour in range(FIRST_BOOKING_HOUR, last_start + 1):
        start_time = f"{hour:02d}:00"
        row.append(InlineKeyboardButton(text=f"🕒 {start_time}", callback_data=f"start_{place}_{hours}_{booking_date}_{start_time}"))
        if len(row) == 3: rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text=t(language, "restart"), callback_data="booking_start")])
    rows.append([InlineKeyboardButton(text=t(language, "cancel_inline"), callback_data="booking_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard(place, hours, booking_date, start_time, language):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(language, "confirm"), callback_data=f"confirm_{place}_{hours}_{booking_date}_{start_time}")],
        [InlineKeyboardButton(text=t(language, "change_choice"), callback_data="booking_start")],
        [InlineKeyboardButton(text=t(language, "cancel_inline"), callback_data="booking_cancel")],
    ])


def retry_booking_keyboard(language: str):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(language, "retry_time"), callback_data="booking_start")]])


def settings_keyboard(language: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(language, "change_language"), callback_data="show_language")],
        [InlineKeyboardButton(text=t(language, "back_main"), callback_data="settings_back")],
    ])
