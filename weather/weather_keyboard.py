from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from main_keyboard import btn_back

btn_weather_simple = KeyboardButton('🌡Температура воздуха')
btn_weather_with_sun = KeyboardButton('☔🌢🌅Полная информация')
bt_location = KeyboardButton('Ваше расположение', request_location=True)
btn_kiev = KeyboardButton('🌃Киев')
btn_other_city = KeyboardButton('🏞Выберите населенный пункт')

weather_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .add(btn_weather_simple, btn_weather_with_sun, btn_back)
weather_prognosus = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .add(KeyboardButton('⌚Текущая')).add(KeyboardButton('👀Прогноз погоды')).add(btn_back)
location_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .add(btn_kiev, btn_other_city, bt_location, btn_back)