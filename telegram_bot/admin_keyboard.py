from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Все брони")],
        [KeyboardButton(text="❌ Удалить бронь")],
        [KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)
