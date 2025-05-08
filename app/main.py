from aiogram import Bot, Dispatcher
from aiogram.fsm import FSMContext
from aiogram.types import Message, CallbackQuery
from config import BOT_TOKEN
from handlers import resident, admin, security

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

dp.include_router(resident.router)
dp.include_router(admin.router)
dp.include_router(security.router)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp)
