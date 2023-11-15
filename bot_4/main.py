# Math bot


# IMPORTS
import os
import json

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
data_path = 'user_data.json'


def get_user_language(id: int) -> str:
    with open(data_path, 'r') as fl:
        file_read = json.load(fl)
    return file_read[str(id)]


# COMMANDS
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer("a")


@dp.message(Command('setlang'))
async def command_set_language_handler(message: Message):
    lang_src, lang_dest = message.text.replace('/setlang', '').strip().split('-')
    user_id = message.from_user.id
    
    try:
        with open(data_path, 'r') as fl:
            file_read = json.load(fl)
    except (FileNotFoundError, json.JSONDecodeError):
        file_read = {}

    if user_id in file_read.keys():
        file_read[str(user_id)] = {
            'src': lang_src, 
            'dest': lang_dest
            }
    else:
        file_read.update(
            {
                str(user_id): 
                    {
                    'src': lang_src, 
                    'dest': lang_dest
                    }
            }
        )

    with open(data_path, 'w') as fl:
        json.dump(file_read, fl, indent=4)


@dp.message(Command('translate'))
async def command_translate_handler(message: Message):
    
    text = message.text.replace('/translate', '')
    langs = get_user_language(message.from_user.id)
    lang_src, lang_dest = langs['src'], langs['dest']
    
    lang_detected = translator.detect()
    text_translated = translator.translate(text, src=lang_src, dest=lang_dest)
    
    await message.answer(f"{text_translated.text}")


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