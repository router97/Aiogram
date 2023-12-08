# MATH BOT


# IMPORTS
from random import randint, choice
from asyncio import run as asyncio_run
from logging import basicConfig, INFO
from sys import stdout
from numpy import safe_eval

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import API_TOKEN


# CONSTANTS
BOT = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
DP = Dispatcher(bot=BOT)
MAX_INCORRECT_TRIES = 5
CORRECT_ANSWERS_TO_WIN = 10


# STATES
class Form(StatesGroup):
    quiz = State()


# FUNCTIONS

# MATH QUIZ GENERATOR
async def generate_quiz(option_count: int = 4) -> dict:
    "Generate a quiz with random options."
    
    # Generate 4 random numbers
    num1, num2, num3, num4 = tuple(randint(1, 9) for _ in range(4))
    
    # Generate a question
    question = f"{num1} {choice(('+', '-', '*', '/'))} {num2}"
    
    # Get the answer
    answer = eval(question)
    
    # Generate 4 random options
    options = [str(eval(f"{answer} {choice(('+', '-', '*', '/'))} {choice((num1, num2, num3, num4))}")) for _ in range(option_count)]

    # Insert the answer in one of the options
    options[randint(0, option_count-1)] = str(answer)
    
    # Return the results
    return {'question': question, 'options': options, 'answer': answer}


# MARKUP GENERATOR
async def generate_quiz_markup(options: list[str]) -> InlineKeyboardMarkup:
    """Generate an inline keyboard markup for the quiz options."""
    
    # Generating buttons
    button_list = [InlineKeyboardButton(text=option, callback_data=option) for option in options]
    
    # Formatting buttons, so that there isn't more than 2 buttons on one line
    button_list_formatted = [button_list[counter:counter+2] for counter in range(0, len(button_list), 2)]
    
    # Return the markup
    return InlineKeyboardMarkup(inline_keyboard=button_list_formatted)


# COMMANDS

# /start
@DP.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    
    # Set state to quiz
    await state.set_state(Form.quiz)
    
    # Generate a quiz
    quiz_math = await generate_quiz()
    
    # Store the quiz and score in state data
    await state.update_data(quiz = quiz_math, score = {'correct': 0, 'incorrect': 0})
    
    # Generate markup
    markup = await generate_quiz_markup(quiz_math['options'])
    
    # Reply
    await message.reply("Sup, i'm a math quiz bot.\n\n<b>5</b> mistakes, you <b>lose</b>\n<b>10</b> correct answers and you <b>win</b>")
    await message.reply(quiz_math['question'], reply_markup=markup)


# CALLBACK QUERY
@DP.callback_query()
async def callback_query_handler(callback_query: types.CallbackQuery, state: FSMContext):
    
    # Fetch the user's data
    state_data = await state.get_data()
    quiz_math = state_data.get('quiz')
    score_user = state_data.get('score', {'correct': 0, 'incorrect': 0})

    # Check if the question is outdated
    if not quiz_math or quiz_math['question'] != callback_query.message.text:
        return await callback_query.answer('outdated question!')
    
    # Check if the data provided is a valid int or float
    # / / / Security check for safe_eval()
    try:
        float(callback_query.data)
    except:
        return
    
    # Fetch the option selected
    selected_option = safe_eval(callback_query.data)
    
    # Answer the query, so that the button won't look like it's frozen
    await callback_query.answer()
    
    # If the selected option is incorrect
    if selected_option != quiz_math['answer']:
        score_user['incorrect'] += 1
        await callback_query.message.edit_text(text=f"<del>{callback_query.message.text}</del>")
        await callback_query.message.reply(f"<b>Incorrect!</b>, the correct option was <b>{quiz_math['answer']}</b>\nYou have <b>{5-score_user['incorrect']}</b> tries left.")
    
    # If it's correct
    else:
        score_user['correct'] += 1
        await callback_query.message.edit_reply_markup()
        await callback_query.message.reply(f"Correct!, your score is <b>{score_user['correct']}/10</b>")
    
    # Check for a loss
    if score_user['incorrect'] >= MAX_INCORRECT_TRIES:
        await state.clear()
        return await callback_query.message.reply('You lost!')
    
    # Check for a win
    elif score_user['correct'] >= CORRECT_ANSWERS_TO_WIN:
        await state.clear()
        return await callback_query.message.reply('You won!')
    
    # Generate a new quiz and markup
    quiz_math = await generate_quiz()
    await state.update_data(quiz = quiz_math, score = score_user)
    markup = await generate_quiz_markup(quiz_math['options'])

    # Send the new message
    await callback_query.message.answer(text=quiz_math['question'], reply_markup=markup)


# LAUNCH
async def main():
    await DP.start_polling(BOT)


if __name__ == "__main__":
    basicConfig(level=INFO, stream=stdout)
    asyncio_run(main())