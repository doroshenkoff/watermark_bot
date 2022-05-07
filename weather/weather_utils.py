from datetime import datetime

import googlemaps
import locale
import requests

import constants

from . import weather_constants as wc


class WeatherHandler:
    def __init__(self):
        self.city = 'Kiev'
        self.lat = None
        self.lon = None


def format_time(time: int):
    return f'0{time}' if time < 10 else time

gmaps = googlemaps.Client(constants.GOOGLE_API_KEY)

def get_location(params: WeatherHandler):

    if params.lat is None:
        try:
            loc = gmaps.geocode(params.city)[0]['geometry']['location']
        except:
            return 'Данный населенный пункт не обнаружен, отображение погоды невозможно...'
        lat, lon = loc['lat'], loc['lng']
    else:
        lat, lon = params.lat, params.lon
    return lat, lon


def weather(params: WeatherHandler, sun=False):
    lat, lon = get_location(params)

    weather_payload = {
        'lat': lat,
        'lon': lon,
        'appid': constants.WEATHER_TOKEN,
        'units': 'metric',
        'lang': 'ru'
    }

    weather = requests.get('https://api.openweathermap.org/data/2.5/weather', weather_payload).json()
    temp = round(weather['main']['temp'], 1)
    conditions = weather['weather'][0]['description'].capitalize()
    elevation = int(gmaps.elevation((lat, lon))[0]['elevation'])

    out = f'🏙 Выбранный населенный пункт - {params.city}\n'
    out += ''
    out += f'🏔 высота - {elevation} м над уровнем моря\n'
    out += ''
    out += f'🌡 Температура воздуха {"+" if temp > 0 else "-" if temp < 0 else ""}{temp}\n'
    out += ''
    out += f"{wc.WEATHER_ICONS.get(weather['weather'][0]['main'], '')} {conditions}"
    if sun:
        d_rise = datetime.fromtimestamp(weather['sys']['sunrise'])
        d_set = datetime.fromtimestamp(weather['sys']['sunset'])
        out += f'\n🌥 облачность - {weather["clouds"]["all"]}%\n'
        out += f'🌬 скорость ветра - {weather["wind"]["speed"]} м/c\n'
        out += f'🌢 влажность воздуха - {weather["main"]["humidity"]}%\n'
        out += f'🫀 атмосферное давление - {int(weather["main"]["pressure"] * 0.750062)} мм рт.ст.\n'
        out += f'🌅 рассвет - {format_time(d_rise.hour)}:{format_time(d_rise.minute)}\n'
        out += f'🌇 закат - {format_time(d_set.hour)}:{format_time(d_set.minute)}'

    return out


def weather_forecast(params: WeatherHandler):
    url = 'https://api.openweathermap.org/data/2.5/onecall'
    lat, lon = get_location(params)
    weather_payload = {
        'lat': lat,
        'lon': lon,
        'appid': constants.WEATHER_TOKEN,
        'units': 'metric',
        'lang': 'ru',
        'exclude': 'current,minutely,hourly,alerts',
    }

    data = requests.get(url, params=weather_payload).json()
    locale.setlocale(locale.LC_ALL, 'ru')
    out = []
    for day in data['daily']:
        sunrise = datetime.fromtimestamp(day['sunrise'])
        sunset = datetime.fromtimestamp(day['sunset'])
        day_light = str(sunset-sunrise).split(':')
        s = f"{datetime.fromtimestamp(day['dt']).strftime('%a, %d.%m')}\n"
        s += f'фаза луны - {wc.MOON_PHASES[int(day["moon_phase"] / 0.125)]}\n'
        s += f'🌅 рассвет - {format_time(sunrise.hour)}:{format_time(sunrise.minute)}\n'
        s += f'🌇 закат - {format_time(sunset.hour)}:{format_time(sunset.minute)}\n'
        s += f'☀ продолжительность светового дня - {day_light[0]} часов, {day_light[1]} минут\n\n'
        s += f'🌡 Температура воздуха {int(day["temp"]["min"])}° ... {int(day["temp"]["max"])}°\n'
        s += f"{wc.WEATHER_ICONS.get(day['weather'][0]['main'], '')} {day['weather'][0]['description']}\n"
        if day.get('rain'):
            s += f'☔Ожидаемые осадки - {day["rain"]} мм, вероятность дождя - {int(day["pop"] * 100)}%\n'
        s += f'🌢 влажность воздуха - {day["humidity"]}%\n'
        s += f'🫀 атмосферное давление - {int(day["pressure"] * 0.750062)} мм рт.ст.\n'
        s += f'🌬 ветер {wc.WIND_DIRECTIONS[day["wind_deg"] // 45]}, ' \
             f'скорость ветра - {int(day["wind_speed"])} м/с, ' \
             f'{day.get("wind_gust") and ("возможны порывы до " + str(int(day["wind_gust"])) + " м/с")}\n'
        out.append(s)
    return out

