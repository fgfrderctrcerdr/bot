import os
import datetime
import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, BotCommandScopeAllPrivateChats, BotCommand
from dotenv import load_dotenv, find_dotenv
from routers import main_router
from cmds import listt_private
from custom_calendar import CustomCalendar  # Ensure you import your custom calendar if needed

load_dotenv(find_dotenv())
# Initialize the bot and dispatcher
bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

# Include routers
dp.include_router(main_router)

async def main_func():
    await bot.delete_webhook(drop_pending_updates=True)  # Remove webhook if set
    await bot.set_my_commands(commands=listt_private, scope=BotCommandScopeAllPrivateChats()) 
    await dp.start_polling(bot)  # Start polling

if __name__ == '__main__':
    asyncio.run(main_func())
