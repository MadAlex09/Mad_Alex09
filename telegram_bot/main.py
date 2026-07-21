import asyncio
import logging
import re
from datetime import date

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, Message

from admin import router as admin_router
from booking import router as booking_router
from config import CLUB_ADDRESS, CLUB_NAME, SUPPORT_USERNAME, TOKEN
from database import (
    create_db,
    delete_user,
    get_user,
    get_user_bookings,
    save_user,
    user_exists,
)
from keyboards import main_menu, phone_keyboard, register_keyboard, remove_keyboard
from settings import COMMON_PRICE, SHOP_ITEMS, VIP_PRICE


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

router = Router(name="main")


class Register(StatesGroup):
    waiting_name = State()
    waiting_phone = State()


def normalize_phone(value: str):
    cleaned = re.sub(r"[^\d+]", "", value.strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    if cleaned.count("+") > 1 or ("+" in cleaned and not cleaned.startswith("+")):
        return None
    digits = re.sub(r"\D", "", cleaned)
    if not 7 <= len(digits) <= 15:
        return None
    return "+" + digits


def format_date(value: str) -> str:
    try:
        return date.fromisoformat(value).strftime("%d.%m.%Y")
    except ValueError:
        return value


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    if user_exists(message.from_user.id):
        user = get_user(message.from_user.id)
        await message.answer(
            f"👋 С возвращением, {user['name']}!\n\n"
            f"Добро пожаловать в {CLUB_NAME}.",
            reply_markup=main_menu,
        )
        return

    await message.answer(
        f"🎮 {CLUB_NAME}\n\n"
        "Здесь можно выбрать компьютер и забронировать удобное время.\n\n"
        "Для начала зарегистрируйтесь.",
        reply_markup=register_keyboard,
    )


@router.message(Command("reset"))
async def reset_registration(message: Message, state: FSMContext) -> None:
    await state.clear()
    delete_user(message.from_user.id)
    await message.answer(
        "🔄 Профиль сброшен. Нажмите кнопку, чтобы зарегистрироваться заново.",
        reply_markup=register_keyboard,
    )


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cancel_action(message: Message, state: FSMContext) -> None:
    await state.clear()
    keyboard = main_menu if user_exists(message.from_user.id) else register_keyboard
    await message.answer("Действие отменено.", reply_markup=keyboard)


@router.message(F.text == "📝 Зарегистрироваться")
async def register_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Register.waiting_name)
    await message.answer(
        "👤 Как вас зовут?",
        reply_markup=remove_keyboard,
    )


@router.message(Register.waiting_name)
async def register_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not 2 <= len(name) <= 60:
        await message.answer("Введите имя длиной от 2 до 60 символов.")
        return

    await state.update_data(name=name)
    await state.set_state(Register.waiting_phone)
    await message.answer(
        "📱 Отправьте номер кнопкой ниже или введите его вручную.\n"
        "Например: +7 777 123 45 67",
        reply_markup=phone_keyboard,
    )


@router.message(Register.waiting_phone)
async def register_phone(message: Message, state: FSMContext) -> None:
    if message.contact:
        if message.contact.user_id not in (None, message.from_user.id):
            await message.answer("Пожалуйста, отправьте свой номер телефона.")
            return
        raw_phone = message.contact.phone_number
    else:
        raw_phone = message.text or ""

    phone = normalize_phone(raw_phone)
    if phone is None:
        await message.answer(
            "Не удалось распознать номер. Введите его в международном формате, "
            "например +7 777 123 45 67."
        )
        return

    data = await state.get_data()
    save_user(message.from_user.id, data["name"], phone)
    await state.clear()
    await message.answer(
        f"✅ Регистрация завершена!\n\nДобро пожаловать, {data['name']}.",
        reply_markup=main_menu,
    )


@router.message(F.text == "💰 Прайс-лист")
async def price_list(message: Message) -> None:
    common = "\n".join(
        f"• {hours} ч. — {price:,} ₸".replace(",", " ")
        for hours, price in COMMON_PRICE.items()
    )
    vip = "\n".join(
        f"• {hours} ч. — {price:,} ₸".replace(",", " ")
        for hours, price in VIP_PRICE.items()
    )
    await message.answer(
        f"💰 Прайс-лист {CLUB_NAME}\n\n"
        f"🖥 Общий зал\n{common}\n\n"
        f"👑 VIP-зал\n{vip}"
    )


@router.message(F.text == "🛒 Магазин")
async def shop(message: Message) -> None:
    await message.answer(
        "🛒 В клубе доступны:\n\n" + "\n".join(SHOP_ITEMS)
    )


@router.message(F.text == "📍 Адрес")
async def address(message: Message) -> None:
    await message.answer(f"📍 {CLUB_ADDRESS}")


@router.message(F.text == "📞 Поддержка")
async def support(message: Message) -> None:
    await message.answer(
        "📞 По вопросам бронирования напишите администратору:\n"
        f"{SUPPORT_USERNAME}"
    )


@router.message(F.text == "👤 Профиль")
async def profile(message: Message) -> None:
    user = get_user(message.from_user.id)
    if user is None:
        await message.answer(
            "Профиль не найден. Зарегистрируйтесь заново.",
            reply_markup=register_keyboard,
        )
        return

    bookings = get_user_bookings(message.from_user.id)
    lines = [
        "👤 Ваш профиль",
        "",
        f"Имя: {user['name']}",
        f"Телефон: {user['phone']}",
    ]

    if bookings:
        lines.extend(["", "🎮 Ваши брони:"])
        for booking in bookings:
            lines.append(
                f"#{booking['id']} · {booking['place']} · "
                f"{format_date(booking['booking_date'])} {booking['start_time']} · "
                f"{booking['hours']} ч."
            )
    else:
        lines.extend(["", "Активных броней пока нет."])

    await message.answer("\n".join(lines))


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Доступные команды:\n"
        "/start — открыть главное меню\n"
        "/cancel — отменить текущее действие\n"
        "/reset — сбросить регистрацию\n"
        "/help — показать помощь"
    )


@router.message(StateFilter(None))
async def unknown_message(message: Message) -> None:
    keyboard = main_menu if user_exists(message.from_user.id) else register_keyboard
    await message.answer(
        "Не понял сообщение. Выберите действие кнопкой ниже.",
        reply_markup=keyboard,
    )


async def configure_bot(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Открыть главное меню"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="cancel", description="Отменить действие"),
            BotCommand(command="reset", description="Сбросить регистрацию"),
        ]
    )


async def run_bot() -> None:
    create_db()
    dispatcher = Dispatcher()
    dispatcher.include_router(admin_router)
    dispatcher.include_router(booking_router)
    dispatcher.include_router(router)

    async with Bot(token=TOKEN) as bot:
        await bot.delete_webhook(drop_pending_updates=False)
        await configure_bot(bot)
        logger.info("Starting %s in polling mode", CLUB_NAME)
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(run_bot())
