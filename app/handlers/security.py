from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
import sqlite3
from aiogram import Bot

router = Router()

def build_request_keyboard(req_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"confirm:{req_id}")
    kb.button(text="❌ Закрыть", callback_data=f"close:{req_id}")
    return kb.as_markup()

@router.message(Command("заявки"))
async def show_requests(message: types.Message):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    cur.execute('''
        SELECT r.id, r.type, r.source, r.method, u.full_name, u.house_number, u.apartment, r.created_at
        FROM requests r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.status = 'new'
        ORDER BY r.created_at DESC
        LIMIT 10
    ''')

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return await message.answer("Нет новых заявок.")

    for row in rows:
        req_id, r_type, source, method, name, house, apt, created = row
        text = (
            f"<b>{r_type.capitalize()}</b> от <b>{name}</b>\n"
            f"Дом {house}, кв. {apt}\n"
            f"{source} — {method}\n"
            f"⏱ {created}"
        )
        await message.answer(text, reply_markup=build_request_keyboard(req_id))

@router.callback_query(F.data.startswith("confirm:"))
async def confirm_request(callback: types.CallbackQuery, bot):
    req_id = int(callback.data.split(":")[1])

    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE requests SET status='confirmed' WHERE id=?", (req_id,))
    conn.commit()

    cur.execute("SELECT user_id FROM requests WHERE id=?", (req_id,))
    user_id = cur.fetchone()[0]
    conn.close()

    await bot.send_message(user_id, "Ваша заявка подтверждена охраной.")
    await callback.answer("Заявка подтверждена")
    await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith("close:"))
async def close_request(callback: types.CallbackQuery, bot):
    req_id = int(callback.data.split(":")[1])

    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE requests SET status='done' WHERE id=?", (req_id,))
    conn.commit()

    cur.execute("SELECT user_id FROM requests WHERE id=?", (req_id,))
    user_id = cur.fetchone()[0]
    conn.close()

    await bot.send_message(user_id, "Ваша заявка выполнена или закрыта.")
    await callback.answer("Заявка закрыта")
    await callback.message.edit_reply_markup(reply_markup=None)
