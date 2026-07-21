from datetime import datetime, timedelta

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import BOT_TIMEZONE
from settings import (
    BOOKING_DAYS,
    BOOKING_DURATIONS,
    COMMON_PC,
    FIRST_BOOKING_HOUR,
    LAST_BOOKING_HOUR,
    VIP_PC,
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎮 Забронировать ПК")],
        [
            KeyboardButton(text="💰 Прайс-лист"),
            KeyboardButton(text="🛒 Магазин"),
        ],
        [
            KeyboardButton(text="👤 Профиль"),
            KeyboardButton(text="📍 Адрес"),
        ],
        [KeyboardButton(text="📞 Поддержка")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)

register_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📝 Зарегистрироваться")]],
    resize_keyboard=True,
)

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить номер", request_contact=True)],
        [KeyboardButton(text="❌ Отмена")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

remove_keyboard = ReplyKeyboardRemove()

hall_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🖥 Общий зал · 20 ПК", callback_data="hall_common")],
        [InlineKeyboardButton(text="👑 VIP-зал · 5 ПК", callback_data="hall_vip")],
        [InlineKeyboardButton(text="✕ Отменить", callback_data="booking_cancel")],
    ]
)


def places_keyboard(kind: str) -> InlineKeyboardMarkup:
    if kind == "common":
        prefix, count, icon = "PC", COMMON_PC, "🖥"
    else:
        prefix, count, icon = "VIP", VIP_PC, "👑"

    rows = []
    row = []
    for number in range(1, count + 1):
        place = f"{prefix}-{number:02d}"
        row.append(
            InlineKeyboardButton(
                text=f"{icon} {place}",
                callback_data=f"place_{place}",
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton(text="← К выбору зала", callback_data="booking_start")])
    rows.append([InlineKeyboardButton(text="✕ Отменить", callback_data="booking_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def duration_keyboard(place: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=f"⏳ {hours} {hour_word(hours)}",
                callback_data=f"duration_{place}_{hours}",
            )
        ]
        for hours in BOOKING_DURATIONS
    ]
    rows.append([InlineKeyboardButton(text="↻ Начать заново", callback_data="booking_start")])
    rows.append([InlineKeyboardButton(text="✕ Отменить", callback_data="booking_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def date_keyboard(place: str, hours: int) -> InlineKeyboardMarkup:
    today = datetime.now(BOT_TIMEZONE).date()
    rows = []
    row = []

    for offset in range(BOOKING_DAYS):
        selected = today + timedelta(days=offset)
        if offset == 0:
            label = "Сегодня"
        elif offset == 1:
            label = "Завтра"
        else:
            label = selected.strftime("%d.%m")

        row.append(
            InlineKeyboardButton(
                text=f"📅 {label}",
                callback_data=f"date_{place}_{hours}_{selected.isoformat()}",
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton(text="↻ Начать заново", callback_data="booking_start")])
    rows.append([InlineKeyboardButton(text="✕ Отменить", callback_data="booking_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def start_time_keyboard(place: str, hours: int, booking_date: str) -> InlineKeyboardMarkup:
    last_start = LAST_BOOKING_HOUR - hours + 1
    rows = []
    row = []

    for hour in range(FIRST_BOOKING_HOUR, last_start + 1):
        start_time = f"{hour:02d}:00"
        row.append(
            InlineKeyboardButton(
                text=f"🕒 {start_time}",
                callback_data=f"start_{place}_{hours}_{booking_date}_{start_time}",
            )
        )
        if len(row) == 3:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton(text="↻ Начать заново", callback_data="booking_start")])
    rows.append([InlineKeyboardButton(text="✕ Отменить", callback_data="booking_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard(
    place: str,
    hours: int,
    booking_date: str,
    start_time: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить бронь",
                    callback_data=(
                        f"confirm_{place}_{hours}_{booking_date}_{start_time}"
                    ),
                )
            ],
            [InlineKeyboardButton(text="↻ Изменить выбор", callback_data="booking_start")],
            [InlineKeyboardButton(text="✕ Отменить", callback_data="booking_cancel")],
        ]
    )


def retry_booking_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Выбрать другое время", callback_data="booking_start")]
        ]
    )


def hour_word(hours: int) -> str:
    if hours == 1:
        return "час"
    if 2 <= hours <= 4:
        return "часа"
    return "часов"
