import os

BAD_WORDS = [
    'хуй',
    'хуёв',
    'хуе',
    'пизд',
    'пидар',
    'блядь',
    'гандон',
    'ебать',
    'ёб',
    'мудак',
    'мудила'
]

ANSWER_FOR_BAD_WORDS = [
    'Матюкаться нехорошо, ублюдок чертов!',
    'Ты не оборзел матом крыть здесь?',
    'Предупреждаю, мат здесь запрещен!',
    'Следи за выражениями, чмо',
    'Нормальным языком можно выражаться?',
    'А без мата можно обойтись, козёл?'
]


DB_TEST = 'sqlite:///videos.db'


WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')

GOOGLE_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

YAHOO_API_KEY = 'KvEw8RIAIt5zqhFjULdTW2UCLWDiUuR039EzKLfY'


# global constants
TOKEN_TELEGRAM = os.getenv('TOKEN_TELEGRAM')

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN_TELEGRAM}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

production = False

timezone = 0 if production else 10800


