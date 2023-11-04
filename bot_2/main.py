# Simple bot, tells the time and says hi



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

from random import randint, choice

# VARIABLES
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)

# COMMANDS
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    print(message, "\n"*3)
    await message.answer("<i>Engie goin' up!</i>\n<b>↓ commands ↓</b>\n<pre>/hello\n/time</pre>")


@dp.message(Command('hello'))
async def command_start_handler(message: Message) -> None:
    print(message, "\n"*3)
    await message.reply(f'Howdy, <b>{message.from_user.full_name}!</b>')


@dp.message(Command('time'))
async def command_start_handler(message: Message) -> None:
    print(message, "\n"*3)
    date = message.date
    await message.reply(f"<pre>GMT-5\nYear: {date.year}.\nMonth: {date.month}.\nDay: {date.day}.\nTime: {date.hour-5} Hours, {date.minute} minutes, {date.second} seconds</pre>")



class PollMath:
    __ops = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y
    }
    
    def __init__(self):
        num1, num2, num3, num4 = randint(1, 11), randint(1, 11), randint(1, 20), randint(1, 11)
        op = choice(['+', '-', '*', '/'])
        self.question = f'{num1} {op} {num2}'
        self.ans = PollMath.__ops[op](num1, num2)
        self.ans_id = randint(1, 4)
        self.opt = [f"{self.ans-num3}", f"{self.ans+num4}", f"{self.ans-num4}", f"{self.ans+num3}"]
        print(self.opt, self.ans, self.ans_id)
        self.opt[self.ans_id-1] = str(self.ans)
        print(self.opt, self.ans, self.ans_id)
    
    def __str__(self):
        return f"question = {self.question}, options = {self.opt}, answer = {self.ans}"


@dp.message(Command('math'))
async def command_math_handler(message: Message) -> None:
    global poll1
    poll1 = PollMath()
    poll = await bot.send_poll(message.chat.id, 
                               question=str(poll1.question), 
                               options=poll1.opt, 
                               is_anonymous=False, 
                               type='quiz', 
                               correct_option_id=poll1.ans_id-1)

@dp.poll_answer()
async def poll_answer_handler(poll_answer: types.PollAnswer):
    user_id = poll_answer.user.id
    option_id = poll_answer.option_ids[0]  # Assuming only one answer is allowed

    if option_id == poll1.ans_id - 1:
        await bot.send_message(user_id, "You answered the quiz correctly!")
    else:
        await bot.send_message(user_id, "Your answer is incorrect. Please try again.")


# MESSAGES
@dp.message()
async def message_handler(message: Message) -> None:
    print(message, "\n"*3)
    await message.reply("Whoops, pal, I reckon I couldn't help with that.\n\nNext time, try typing <b>/hello</b>, or <b>/time</b>, <i>perhaps?</i>")



# LAUNCH
async def main() -> None:
    bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())