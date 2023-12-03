# AIOGRAM WEATHER BOT


# IMPORTS
from sys import stdout
from asyncio import run as asyncio_run
from logging import basicConfig, INFO
from requests import get as requests_get

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from geopy import Nominatim

from config import API_TOKEN, API_WEATHER


# VARIABLES
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot=bot)
form_router = Router(name='Weather FSM machine')
geolocator = Nominatim(user_agent='bot')


# FUNCTIONS
def get_weather_by_city(city: str) -> dict | None:
    """Get a json response from openweather API by city name"""
    
    # Make a GET request to the OpenWeatherMap API
    response = requests_get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_WEATHER}")

    # Return the dictionary
    return response.json() if response else None


def generate_weather_message(weather_data: dict, city: str) -> str:
    """Generate a message, providing the current weather status"""
    
    # Convert the temperature to Celsius
    temperature_in_celsius = weather_data['main']['temp'] - 273.15
    
    # Extract the weather description
    weather_description = weather_data['weather'][0]['description']
    
    # Extract the wind speed
    wind_speed = weather_data['wind']['speed']
    
    # Extract the humidity
    humidity = weather_data['main']['humidity']
    
    # Return the message
    return f"""Weather in <b>{city}</b>\n
Temperature: <b>{temperature_in_celsius:.2f}°C</b>
Weather: <b>{weather_description}</b>
Wind Speed: <b>{wind_speed} m/s</b>
Humidity: <b>{humidity}%</b>
"""


# STATES
class Form(StatesGroup):
    city = State()


# /start handler
@form_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    """/start handler"""
    
    # Setting state to city
    await state.set_state(Form.city)
    
    # Greeting the user and asking for the location
    await message.answer(
        f"sup, {message.from_user.first_name}, send me your location or city name and i'll handle the rest.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Send Location", request_location=True),
                    types.KeyboardButton(text="Cancel")
                ]
            ],
            resize_keyboard=True
        )
    )


# Cancel handler
@form_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext):
    """Cancel handler"""
    
    # Clearing the states
    await state.clear()
    
    # Sending a message
    await message.reply(
        "aight",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard = [
                [
                    types.KeyboardButton(text='/start')
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


# Message handler (location or city name)
@form_router.message()
async def process_location(message: Message, state: FSMContext):
    """City name or location handler"""
    
    # If the message is a location
    if message.location:
        
        # Fetch the latitude and longitude
        coordinates = message.location.latitude, message.location.longitude
        
        # Get the city name
        try:
            city = geolocator.reverse(coordinates, language='en').raw['address'].get('city', '')
        except:
            return await message.reply('invalid location')
    
    # If it's not a location
    else:
        
        # Fetch the city name
        city = message.text.casefold()
    
    # Updating the city name state
    await state.update_data(city = city)
    
    # Getting the API response
    weather_data = get_weather_by_city(city)
    
    # Checking if the city name isn't valid
    if not weather_data:
        return message.reply('invalid city name or location')
    
    # Generate a message
    message_weather = generate_weather_message(weather_data, city)

    # Send the message, with an inline button to update the weather
    await message.reply(
        message_weather,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="Update", callback_data='update')
                ]
            ]
        )
    )


# Update weather handler
@form_router.callback_query(lambda c : c.data == 'update')
async def update_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Inline update button handler"""
    
    # Getting city name from state
    city = await state.get_data()
    city = city.get('city')
    
    # Checking if the city is set
    if not city:
        return
    
    # Getting the API response
    weather_data = get_weather_by_city(city)
    
    # Generate a message
    new_message = generate_weather_message(weather_data, city)
    
    # Check if anything changed
    if new_message != callback_query.message.text:
        
        # Updating the message with up-to-date weather
        await callback_query.message.edit_text(new_message)
        await callback_query.message.edit_reply_markup(
            reply_markup = types.InlineKeyboardMarkup(
            inline_keyboard=[
                    [
                        types.InlineKeyboardButton(text="Update", callback_data='update')
                    ]
                ]
            )
        )


# LAUNCH
async def main():
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    basicConfig(level=INFO, stream=stdout)
    asyncio_run(main())