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

from random import randint, choice, shuffle

from config import API_TOKEN


# VARIABLES
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)


# COMMANDS
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    print(message, "\n"*3)
    await message.answer("<i>Engie goin' up!</i>\n<b>↓ commands ↓</b>\n<pre>/math</pre>")


def generate_math_questions() -> tuple[list, str]:
    "Generates 4 random questions, and an answer to one of them."
    
    num1, num2, num3, num4 = randint(1, 11), randint(1, 11), randint(1, 20), randint(1, 20)
    op1, op2 = choice(['+', '-', '*', '/']), choice(['+', '-', '*', '/'])
    length = randint(2,3)
    question_real = f"{num1}{op1}{num2}"
    question2, question3, question4 = f"{num2}{op1}{num4+num2}", f"{num4*num1}{op2}{num4*num1}", f"{num1}{op1}{num1+num3}"
    rand = randint(0,3)
    options = [question_real, question2, question3, question4]
    options[randint(0,3)] += f"{op2}{num4}"
    options[randint(0,3)] += f"{op2}{num4}"
    answer = f"{eval(options[0])}"
    shuffle(options)
    return options, answer


def generate_message() -> InlineKeyboardMarkup:
    """Generates a message markup and changes the global answer."""
    
    global answer
    options, answer = generate_math_questions()
    button = InlineKeyboardButton(text=options[0], callback_data=options[0])
    button2 = InlineKeyboardButton(text=options[1], callback_data=options[1])
    button3 = InlineKeyboardButton(text=options[2], callback_data=options[2])
    button4 = InlineKeyboardButton(text=options[3], callback_data=options[3])
    button5 = InlineKeyboardButton(text='next', callback_data='next')
    markup = InlineKeyboardMarkup(inline_keyboard=[[button,button2], [button3, button4], [button5]])
    return markup


@dp.message(Command('math'))
async def command_math_handler(message: Message):
    
    global answer
    markup = generate_message()
    await message.reply(text=f"{answer}", reply_markup=markup)


@dp.callback_query(lambda c: True)
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    
    selected_option = query.data
    
    if str(eval(selected_option)) == answer:
        await query.answer("Correct!")
    elif selected_option == 'next':
        markup = generate_message()
        await query.message.edit_text(text=f"{answer}", reply_markup=markup)
    else:
        await query.answer("Incorrect!")


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