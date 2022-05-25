from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
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


period_data = CallbackData('period', 'data')

period_kb = InlineKeyboardMarkup(resize_keyboard=True).add(
    InlineKeyboardButton('Сегодня', callback_data=period_data.new(data='0')),
    InlineKeyboardButton('Завтра', callback_data=period_data.new(data='1')),
    InlineKeyboardButton('3 дня', callback_data=period_data.new(data='3')),
    InlineKeyboardButton('5 дней', callback_data=period_data.new(data='5')),
    InlineKeyboardButton('7 дней', callback_data=period_data.new(data='7'))
)

hour_forecast_kb = InlineKeyboardMarkup().add\
    (InlineKeyboardButton('Подробный прогноз', callback_data=period_data.new(data='8')))


