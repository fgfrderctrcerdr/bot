import os
import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from dotenv import load_dotenv, find_dotenv
from routers import main_router
from custom_calendar import CustomCalendar  # Убедитесь, что импортируете кастомный календарь при необходимости

# Загрузка переменных окружения из файла .env
load_dotenv(find_dotenv())

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

# Включение маршрутов
dp.include_router(main_router)

async def main_func():
    await bot.delete_webhook(drop_pending_updates=True)  # Удаление webhook, если он был установлен
    await dp.start_polling(bot)  # Запуск бота

if __name__ == '__main__':
    asyncio.run(main_func())
