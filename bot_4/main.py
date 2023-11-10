# Math bot


# IMPORTS
from aiogram import Bot, Dispatcher
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from googletrans import Translator

from config import API_TOKEN


# VARIABLES
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)
translator = Translator()


# COMMANDS
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    print(message, "\n"*3)
    await message.answer("<i>Engie goin' up!</i>\n<b>↓ commands ↓</b>\n<pre>/math</pre>")


@dp.message(Command('translate'))
async def command_translate_handler(message: Message):
    text = message.text.replace('/translate', '')
    text_translated = translator.translate(text)
    await message.answer(f"↓ Translated from <b>{text_translated.src}</b> to <b>{text_translated.dest}</b> ↓\n<code>{text_translated.text}</code>")


# MESSAGES
@dp.message()
async def message_handler(message: Message):
    print(message, "\n"*3)
    await message.reply("Whoops, pal, I reckon I couldn't help with that.\n\nNext time, try typing <b>/math</b>, <i>perhaps?</i>")


# LAUNCH
async def main():
    bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())