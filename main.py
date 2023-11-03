from aiogram import Bot, Dispatcher
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from token_1 import API_TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    print(message)
    print(message.chat)
    await message.answer("<i>Engie goin' up!</i>\n<b>↓ commands ↓</b>\n<pre>/hello\n/time</pre>")


@dp.message(Command('hello'))
async def command_start_handler(message: Message) -> None:
    print(message)
    print(message.chat)
    await message.reply(f'Howdy, <b>{message.from_user.full_name}!</b>')


@dp.message(Command('time'))
async def command_start_handler(message: Message) -> None:
    print(message)
    print(message.chat)
    date = message.date
    await message.reply(f"<pre>GMT-5\nYear: {date.year}.\nMonth: {date.month}.\nDay: {date.day}.\nTime: {date.hour-5} Hours, {date.minute} minutes, {date.second} seconds</pre>")


@dp.message()
async def message_handler(message: Message) -> None:
    await message.reply("Whoops, pal, I reckon I couldn't help with that.\n\nNext time, try typing <b>/hello</b>, or <b>/time</b>, <i>perhaps?</i>")

async def main() -> None:
    bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())