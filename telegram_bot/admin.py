from datetime import date
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from admin_keyboard import admin_menu
from config import ADMIN_ID
from database import delete_booking, get_all_bookings, get_user_language
from keyboards import main_menu

router = Router(name="admin")
class AdminDelete(StatesGroup): waiting_booking_id = State()
def is_admin(message): return message.from_user.id == ADMIN_ID
def display_date(value):
    try: return date.fromisoformat(value).strftime("%d.%m.%Y")
    except ValueError: return value
async def send_bookings(message):
    rows = get_all_bookings()
    if not rows: await message.answer("📋 Активных броней пока нет.", reply_markup=admin_menu); return
    chunks=[]; current="📋 Последние брони:\n\n"
    for row in rows:
        entry=f"#{row['id']} · {row['name']}\n{row['place']} · {row['hours']} ч.\n{display_date(row['booking_date'])} · {row['start_time']}\n────────────\n"
        if len(current)+len(entry)>3900: chunks.append(current); current=entry
        else: current+=entry
    if current: chunks.append(current)
    for i, chunk in enumerate(chunks): await message.answer(chunk, reply_markup=admin_menu if i==len(chunks)-1 else None)
@router.message(Command("admin"))
async def admin_panel(message, state):
    if not is_admin(message): await message.answer("❌ Нет доступа."); return
    await state.clear(); await message.answer("👑 Панель администратора", reply_markup=admin_menu)
@router.message(Command("bookings"))
@router.message(F.text == "📋 Все брони")
async def bookings(message: Message):
    if not is_admin(message): await message.answer("❌ Нет доступа."); return
    await send_bookings(message)
@router.message(F.text == "❌ Удалить бронь")
async def delete_booking_start(message: Message, state: FSMContext):
    if not is_admin(message): return
    await state.set_state(AdminDelete.waiting_booking_id); await message.answer("Введите номер брони, которую нужно удалить.\nНапример: 12")
@router.message(AdminDelete.waiting_booking_id)
async def delete_booking_finish(message: Message, state: FSMContext):
    if not is_admin(message): await state.clear(); return
    value=(message.text or "").strip().removeprefix("#")
    if not value.isdigit(): await message.answer("Введите только номер брони, например 12."); return
    booking_id=int(value); deleted=delete_booking(booking_id); await state.clear()
    await message.answer(f"✅ Бронь #{booking_id} удалена." if deleted else "❌ Бронь с таким номером не найдена.", reply_markup=admin_menu)
@router.message(F.text == "🏠 Главное меню")
async def leave_admin(message: Message, state: FSMContext):
    if not is_admin(message): return
    await state.clear(); await message.answer("Главное меню", reply_markup=main_menu(get_user_language(message.from_user.id)))
