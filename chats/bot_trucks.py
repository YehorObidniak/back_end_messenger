from aiogram import executor, Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

DEPARTMENT_NAME = 'Trucks'

token = '6192660501:AAGG8xAU8fhnmDDUM-1eTIisNUEKNY7jeq0'
bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def send_message(user_id, text):
    message = await bot.send_message(chat_id=user_id, text=text)
    return message.message_id

if __name__ == "__main__":
    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        pass