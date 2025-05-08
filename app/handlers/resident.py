from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import is_code_valid, mark_code_used, add_user, add_request
from keyboards.resident_kb import main_menu_kb
from config import SECURITY_IDS
from aiogram import Bot

router = Router()

class RegState(StatesGroup):
    waiting_for_code = State()
    waiting_for_house = State()
    waiting_for_apartment = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Введите код доступа:")
    await state.set_state(RegState.waiting_for_code)

@router.message(RegState.waiting_for_code)
async def check_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    if not is_code_valid(code):
        return await message.answer("Неверный или использованный код.")
    
    mark_code_used(code)
    await message.answer("Код принят. Введите номер вашего дома (1-4):")
    await state.set_state(RegState.waiting_for_house)

@router.message(RegState.waiting_for_house)
async def get_house_number(message: types.Message, state: FSMContext):
    try:
        house = int(message.text)
        if house not in [1, 2, 3, 4]:
            raise ValueError
    except ValueError:
        return await message.answer("Введите корректный номер дома (1-4).")

    await state.update_data(house=house)
    await message.answer("Теперь введите номер вашей квартиры:")
    await state.set_state(RegState.waiting_for_apartment)

@router.message(RegState.waiting_for_apartment)
async def get_apartment(message: types.Message, state: FSMContext):
    apartment = message.text.strip()
    if not apartment:
        return await message.answer("Пожалуйста, введите номер квартиры.")

    data = await state.get_data()
    user = message.from_user

    add_user(
        user_id=user.id,
        full_name=user.full_name,
        house_number=data['house'],
        apartment=apartment
    )

    await message.answer("Регистрация завершена!", reply_markup=main_menu_kb())
    await state.clear()

@router.message(Command("оставить заявку"))
async def create_request(message: types.Message):
    # Пример создания заявки
    r_type = "доставка"  # или получаем из выбора пользователя
    source = "Ozon"  # например, получаем из выбора
    method = "оставить у двери"  # способ доставки

    # Добавление заявки в базу данных
    add_request(message.from_user.id, r_type, source, method)

    # Уведомление охране
    bot = Bot(token="YOUR_BOT_TOKEN")
    for security_id in SECURITY_IDS:
        await bot.send_message(security_id, f"Новая заявка от {message.from_user.full_name}:\n"
                                           f"Тип: {r_type}\nИсточник: {source}\nМетод: {method}\n"
                                           f"Дом: {message.from_user.id}, Кв: {message.text}")

    await message.answer("Ваша заявка успешно отправлена и будет обработана.")
