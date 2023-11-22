# IMPORTS
from aiogram import Bot, Dispatcher
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import API_TOKEN



# VARIABLES
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)


# LAUNCH
async def main() -> None:
    bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())