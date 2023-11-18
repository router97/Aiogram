# Translator Bot


# IMPORTS
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from googletrans import Translator

from config import API_TOKEN




# VARIABLES
bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot=bot)
translator = Translator()
form_router = Router()




# STATES
class Form(StatesGroup):
    activate = State()
    lang_src = State()
    lang_dest = State()
    translating = State()




# HANDLERS


# /start handler
@form_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    # Asking whether to proceed or not
    await state.set_state(Form.activate)
    await message.answer(
        "sup, I can translate stuff for you, wanna proceed?",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Yes"),
                    types.KeyboardButton(text="No")
                ]
            ],
            resize_keyboard=True,
        ),
    )


# Activation no handler
@form_router.message(Form.activate, F.text.casefold() == "no")
async def process_activate_no(message: Message, state: FSMContext):
    await state.update_data(activate = message.text)

    await message.reply(
        "cya later, then",
        reply_markup=types.ReplyKeyboardRemove()
        )


# Activation yes handler / Asking for source language
@form_router.message(Form.activate, F.text.casefold() == "yes")
async def process_activate_yes(message: Message, state: FSMContext):
    await state.update_data(activate = message.text)
    await state.set_state(Form.lang_src)

    # Asking for the source language and adding a keyboard option to auto-detect the language
    await message.reply(
        'ok, type the language to translate from (example: "en" or "uk")',
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Auto"),
                    types.KeyboardButton(text="Cancel")
                ]
            ],
            resize_keyboard=True
        ),
    )


# Cancel handler
@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def process_cancel(message: Message, state: FSMContext):
    # Clear all states and return to beginning
    await state.clear()
    await message.answer(
        "cya",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="/start")
                ]
            ],
            resize_keyboard=True
        ),
    )


# Asking for destination language
@form_router.message(Form.lang_src)
async def process_lang_src(message: Message, state: FSMContext):
    await state.update_data(lang_src=message.text)
    await state.set_state(Form.lang_dest)

    # Asking for the destination language
    await message.reply(
        'okay, now, the language to translate to (example: "en" or "uk")',
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Cancel")
                ]
            ],
            resize_keyboard=True
        ),
    )


# Finish changing language
@form_router.message(Form.lang_dest)
async def process_lang_dest(message: Message, state: FSMContext):
    await state.update_data(lang_dest=message.text)
    # Setting the state to translating
    await state.set_state(Form.translating)
    
    # Reply to indicate finishing setting up the language
    await message.reply("aight, now, just type something and I'll translate it",
                        reply_markup=types.ReplyKeyboardMarkup(
                            keyboard=[
                                [
                                    types.KeyboardButton(text="Change Language"),
                                    types.KeyboardButton(text="Cancel")
                                ]
                            ],
                            resize_keyboard=True
                        )
    )


# Translating
@form_router.message(Form.translating, F.text.casefold() != "change language")
async def translate(message: Message, state: FSMContext):
    # Fetching language data
    data = await state.get_data()
    lang_src = data.get("lang_src", "auto")
    lang_dest = data.get("lang_dest", "en") 
    
    # Translating and sending the result
    try:
        text_translated = translator.translate(
            # Setting the source language, or giving None if auto
            src = lang_src if lang_src != 'auto' else None, 
            dest = lang_dest, 
            text = message.text
        )
        
        # Sending the translated text with a keyboard option to change the language
        await message.reply(
            text_translated.text,
            reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Change Language"), 
                    types.KeyboardButton(text="Cancel")
                ]
            ],
            resize_keyboard=True
            )
        )
    
    except ValueError:
        # Language error handler
        await message.reply(f'invalid language! Yours are: {lang_src}-{lang_dest}',
                            reply_markup=types.ReplyKeyboardMarkup(
                            keyboard=[
                                [
                                    types.KeyboardButton(text="Change Language"), 
                                    types.KeyboardButton(text="Cancel")
                                ]
                            ],
                            resize_keyboard=True
                            )
        )


# Change language from translating
@form_router.message(Form.translating, F.text.casefold() == "change language")
async def process_translating_change(message: Message, state: FSMContext):
    await state.set_state(Form.lang_src)

    # Asking for the source language or a keyboard option for auto-detection
    await message.reply(
        'type your source language (example: "en" or "uk")',
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Auto"), 
                    types.KeyboardButton(text="Cancel")
                ]
            ],
            resize_keyboard=True
        ) 
    )




# LAUNCH


async def main():
    # Routers
    dp.include_router(form_router)
    
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Logging
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Launching the bot
    asyncio.run(main())