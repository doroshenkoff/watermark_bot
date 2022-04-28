import requests
import constants
import pytz
from datetime import datetime


class WeatherHandler:
    def __init__(self):
        self.city = 'Kiev'
        self.lat = None
        self.lon = None


def format_time(time: int):
    return f'0{time}' if time < 10 else time


def weather(params: WeatherHandler, sun=False):

    if params.lat is None:
        geo_payload = {
            'q': params.city,
            'appid': constants.WEATHER_TOKEN
        }
        geo_responce = requests.get('http://api.openweathermap.org/geo/1.0/direct', geo_payload).json()[0]
        lat, lon = geo_responce['lat'], geo_responce['lon']
    else:
        lat, lon = params.lat, params.lon

    weather_payload = {
        'lat': lat,
        'lon': lon,
        'appid': constants.WEATHER_TOKEN,
        'units': 'metric',
        'lang': 'ru'
    }

    weather = requests.get('https://api.openweathermap.org/data/2.5/weather', weather_payload).json()
    temp = round(weather['main']['temp'], 1)
    conditions = weather['weather'][0]['description']

    out = f'🏙 населенный пункт - {weather["name"]}'
    out += '\n'
    out += f'🌡 Температура воздуха {"+" if temp > 0 else "-" if temp < 0 else ""}{temp}, {conditions}'

    if sun:
        d_rise = datetime.fromtimestamp(weather['sys']['sunrise'])
        d_set = datetime.fromtimestamp(weather['sys']['sunset'])
        out += '\n'
        out += f'🌥 облачность - {weather["clouds"]["all"]}%'
        out += '\n'
        out += f'🌬 скорость ветра - {weather["wind"]["speed"]} м/c'
        # , порывы до {weather["wind"]["gust"]} м/с
        out += '\n'
        out += f'🌢 влажность воздуха - {weather["main"]["humidity"]}%'
        out += '\n'
        out += f'🫀 атмосферное давление - {int(weather["main"]["pressure"] * 0.750062)} мм рт.ст.'
        out += '\n'
        out += f'🌅 рассвет - {format_time(d_rise.hour)}:{format_time(d_rise.minute)}'
        out += '\n'
        out += f'🌇 закат - {format_time(d_set.hour)}:{format_time(d_set.minute)}'

    return out


def currency_foreign():
    url = 'https://www.alphavantage.co/query'
    cur_list = {'EUR': '€', 'BTC': '₿'}
    out = ''
    for cur, s in cur_list.items():
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': cur,
            'to_currency': 'USD',
            'apikey': '3USL4E2ZBH9NMYE3'
        }
        data = requests.get(url=url, params=params).json()['Realtime Currency Exchange Rate']
        out += f'{s} {data["2. From_Currency Name"]} - {round(float(data["5. Exchange Rate"]), 4)} 💲'
        out += '\n'
    return out


if __name__ == '__main__':
    print(currency_foreign())
