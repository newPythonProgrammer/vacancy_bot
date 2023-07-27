from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from handlers.client import register_client
from handlers.admin import register_admin
import config

bot = Bot(config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

async def main(_):#Функция выполняется при запуске
    for admin in config.ADMINS:
        try:
            await bot.send_message(admin, 'Бот запущен!')
        except:
            pass


register_client(dp)
register_admin(dp)
executor.start_polling(dp, on_startup=main)