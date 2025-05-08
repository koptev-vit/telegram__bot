from aiogram import Router, types, F
from aiogram.filters import Command
from config import ADMIN_IDS
import sqlite3
import random
import string

router = Router()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("У вас нет доступа.")
    
    text = (
        "🔧 Панель администратора:\n"
        "/newcode — создать код доступа\n"
        "/users — список жильцов\n"
        "/codes — список кодов"
    )
    await message.answer(text)

@router.message(Command("newcode"))
async def new_code(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("У вас нет доступа.")
    
    code = generate_code()
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO access_codes (code, used) VALUES (?, 0)", (code,))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Новый код доступа: `{code}`", parse_mode="Markdown")

@router.message(Command("users"))
async def list_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("У вас нет доступа.")
    
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT full_name, house_number, apartment, role FROM users")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return await message.answer("Нет зарегистрированных пользователей.")

    text = "👥 Зарегистрированные пользователи:\n"
    for row in rows:
        name, house, apt, role = row
        text += f"{name} — Дом {house}, кв. {apt} ({role})\n"
    
    await message.answer(text)

@router.message(Command("codes"))
async def list_codes(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("У вас нет доступа.")
    
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT code, used FROM access_codes")
    codes = cur.fetchall()
    conn.close()

    if not codes:
        return await message.answer("Нет кодов в базе.")

    text = "🔐 Коды доступа:\n"
    for code, used in codes:
        status = "✅" if used else "❌"
        text += f"{code} — {status}\n"

    await message.answer(text)
