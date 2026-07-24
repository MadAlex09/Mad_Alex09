import asyncio
import logging
import re
from datetime import date
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, CallbackQuery, Message
from admin import router as admin_router
from booking import router as booking_router
from config import CLUB_ADDRESS, CLUB_NAME, SUPPORT_USERNAME, TOKEN
from database import create_db, delete_user, get_user, get_user_bookings, get_user_language, has_language_choice, save_user, set_user_language, user_exists
from keyboards import language_keyboard, main_menu, phone_keyboard, register_keyboard, remove_keyboard, settings_keyboard
from settings import COMMON_PRICE, SHOP_ITEMS, VIP_PRICE
from translations import hour_word, t

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)
router = Router(name="main")

class Register(StatesGroup):
    waiting_name = State(); waiting_phone = State()

def normalize_phone(value: str):
    cleaned = re.sub(r"[^\d+]", "", value.strip())
    if cleaned.startswith("00"): cleaned = "+" + cleaned[2:]
    if cleaned.count("+") > 1 or ("+" in cleaned and not cleaned.startswith("+")): return None
    digits = re.sub(r"\D", "", cleaned)
    return "+" + digits if 7 <= len(digits) <= 15 else None

def format_date(value: str) -> str:
    try: return date.fromisoformat(value).strftime("%d.%m.%Y")
    except ValueError: return value

def lang(user_id: int) -> str: return get_user_language(user_id)

async def show_home(message: Message, language: str, user_id: int | None = None) -> None:
    # For regular messages message.from_user is the user.
    # For callback.message it is the bot itself, so callback.from_user.id
    # must be passed explicitly.
    telegram_id = user_id if user_id is not None else message.from_user.id
    user = get_user(telegram_id)
    if user:
        await message.answer(
            t(language, "welcome_back", name=user["name"], club=CLUB_NAME),
            reply_markup=main_menu(language),
        )
    else:
        await message.answer(
            t(language, "new_welcome", club=CLUB_NAME),
            reply_markup=register_keyboard(language),
        )

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    if not has_language_choice(message.from_user.id):
        await message.answer(t("en", "choose_language"), reply_markup=language_keyboard); return
    await show_home(message, lang(message.from_user.id))

@router.message(Command("language"))
async def language_command(message: Message):
    await message.answer(t(lang(message.from_user.id), "choose_language"), reply_markup=language_keyboard)

@router.callback_query(F.data.startswith("language_"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    language = callback.data.removeprefix("language_")
    set_user_language(callback.from_user.id, language)
    await state.clear()
    await callback.message.edit_text(t(language, "language_changed"))
    await show_home(callback.message, language, callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "show_language")
async def show_language(callback: CallbackQuery):
    await callback.message.edit_text(t(lang(callback.from_user.id), "choose_language"), reply_markup=language_keyboard); await callback.answer()

@router.callback_query(F.data == "settings_back")
async def settings_back(callback: CallbackQuery):
    language = lang(callback.from_user.id)
    await callback.message.edit_text(t(language, "language_changed"))
    await callback.message.answer(t(language, "welcome_back", name=get_user(callback.from_user.id)["name"], club=CLUB_NAME), reply_markup=main_menu(language)); await callback.answer()

@router.message(Command("reset"))
async def reset_registration(message: Message, state: FSMContext):
    await state.clear(); delete_user(message.from_user.id)
    await message.answer(t("en", "profile_reset"), reply_markup=language_keyboard)

@router.message(Command("cancel"))
@router.message(F.text.in_({"❌ Cancel", "❌ Отмена"}))
async def cancel_action(message: Message, state: FSMContext):
    await state.clear(); language = lang(message.from_user.id)
    keyboard = main_menu(language) if user_exists(message.from_user.id) else register_keyboard(language)
    await message.answer(t(language, "cancelled"), reply_markup=keyboard)

@router.message(F.text.in_({"📝 Register", "📝 Зарегистрироваться"}))
async def register_start(message: Message, state: FSMContext):
    language = lang(message.from_user.id); await state.set_state(Register.waiting_name)
    await message.answer(t(language, "ask_name"), reply_markup=remove_keyboard)

@router.message(Register.waiting_name)
async def register_name(message: Message, state: FSMContext):
    language = lang(message.from_user.id); name = (message.text or "").strip()
    if not 2 <= len(name) <= 60: await message.answer(t(language, "invalid_name")); return
    await state.update_data(name=name); await state.set_state(Register.waiting_phone)
    await message.answer(t(language, "ask_phone"), reply_markup=phone_keyboard(language))

@router.message(Register.waiting_phone)
async def register_phone(message: Message, state: FSMContext):
    language = lang(message.from_user.id)
    if message.contact:
        if message.contact.user_id not in (None, message.from_user.id): await message.answer(t(language, "own_phone")); return
        raw_phone = message.contact.phone_number
    else: raw_phone = message.text or ""
    phone = normalize_phone(raw_phone)
    if phone is None: await message.answer(t(language, "invalid_phone")); return
    data = await state.get_data(); save_user(message.from_user.id, data["name"], phone); await state.clear()
    await message.answer(t(language, "registration_done", name=data["name"]), reply_markup=main_menu(language))

@router.message(F.text.in_({"💰 Price list", "💰 Прайс-лист"}))
async def price_list(message: Message):
    language = lang(message.from_user.id)
    common = "\n".join(f"• {hours} {t(language, 'hour_short')} — {price:,} ₸".replace(",", " ") for hours, price in COMMON_PRICE.items())
    vip = "\n".join(f"• {hours} {t(language, 'hour_short')} — {price:,} ₸".replace(",", " ") for hours, price in VIP_PRICE.items())
    await message.answer(f"{t(language, 'price_title', club=CLUB_NAME)}\n\n{t(language, 'common_hall')}\n{common}\n\n{t(language, 'vip_hall')}\n{vip}")

@router.message(F.text.in_({"🛒 Shop", "🛒 Магазин"}))
async def shop(message: Message):
    language = lang(message.from_user.id)
    items = SHOP_ITEMS.get(language, SHOP_ITEMS["en"])
    await message.answer(t(language, "shop_title") + "\n\n" + "\n".join(items))

@router.message(F.text.in_({"📍 Address", "📍 Адрес"}))
async def address(message: Message):
    language = lang(message.from_user.id)
    await message.answer(t(language, "address", address=CLUB_ADDRESS))

@router.message(F.text.in_({"📞 Support", "📞 Поддержка"}))
async def support(message: Message):
    language = lang(message.from_user.id); await message.answer(t(language, "support", username=SUPPORT_USERNAME))

@router.message(F.text.in_({"⚙️ Settings", "⚙️ Настройки"}))
async def settings(message: Message):
    language = lang(message.from_user.id); await message.answer(t(language, "settings_title"), reply_markup=settings_keyboard(language))

@router.message(F.text.in_({"👤 Profile", "👤 Профиль"}))
async def profile(message: Message):
    language = lang(message.from_user.id); user = get_user(message.from_user.id)
    if user is None: await message.answer(t(language, "profile_missing"), reply_markup=register_keyboard(language)); return
    bookings = get_user_bookings(message.from_user.id)
    lines = [t(language, "profile_title"), "", f"{t(language, 'name')}: {user['name']}", f"{t(language, 'phone')}: {user['phone']}"]
    if bookings:
        lines.extend(["", t(language, "your_bookings")])
        for b in bookings: lines.append(f"#{b['id']} · {b['place']} · {format_date(b['booking_date'])} {b['start_time']} · {b['hours']} {t(language, 'hour_short')}")
    else: lines.extend(["", t(language, "no_bookings")])
    await message.answer("\n".join(lines))

@router.message(Command("help"))
async def help_command(message: Message): await message.answer(t(lang(message.from_user.id), "help"))

@router.message(StateFilter(None))
async def unknown_message(message: Message):
    language = lang(message.from_user.id); keyboard = main_menu(language) if user_exists(message.from_user.id) else register_keyboard(language)
    await message.answer(t(language, "unknown"), reply_markup=keyboard)

async def configure_bot(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Open main menu"), BotCommand(command="help", description="Help"),
        BotCommand(command="language", description="Change language"), BotCommand(command="cancel", description="Cancel action"),
        BotCommand(command="reset", description="Reset registration"),
    ])

async def run_bot():
    create_db(); dispatcher = Dispatcher(); dispatcher.include_router(admin_router); dispatcher.include_router(booking_router); dispatcher.include_router(router)
    async with Bot(token=TOKEN) as bot:
        await bot.delete_webhook(drop_pending_updates=False); await configure_bot(bot)
        logger.info("Starting %s in polling mode", CLUB_NAME)
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())

if __name__ == "__main__": asyncio.run(run_bot())
