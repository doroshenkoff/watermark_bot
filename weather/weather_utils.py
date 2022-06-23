from datetime import datetime

import googlemaps
import locale
import requests

import config

from . import weather_constants as wc


class WeatherHandler:
    def __init__(self, city='Kiev', lat=None, lon=None):
        self.city = city
        self.lat = lat
        self.lon = lon


def format_time(time: int):
    return f'0{time}' if time < 10 else time


gmaps = googlemaps.Client(config.GOOGLE_API_KEY)


def get_location(params: WeatherHandler):
    if params.lat is None:
        try:
            loc = gmaps.geocode(params.city)[0]['geometry']['location']
        except:
            return None
        lat, lon = loc['lat'], loc['lng']
    else:
        lat, lon = params.lat, params.lon
    return lat, lon


def get_air_pollution(lat, lon):
    try:
        data = requests.get('http://api.openweathermap.org/data/2.5/air_pollution',
                            params={'lat': lat,
                                    'lon': lon,
                                    'appid': config.WEATHER_TOKEN}) \
            .json()
        index = data['list'][0]['main']['aqi']
        return ''.join('★' if i < 6 - index else '✩' for i in range(5))
    except:
        return 'нет данных'


def weather(params: WeatherHandler, sun=False):
    lat, lon = get_location(params)

    weather_payload = {
        'lat': lat,
        'lon': lon,
        'appid': config.WEATHER_TOKEN,
        'units': 'metric',
        'lang': 'ru'
    }

    weather = requests.get('https://api.openweathermap.org/data/2.5/weather', weather_payload).json()
    temp = round(weather['main']['temp'], 1)
    conditions = weather['weather'][0]['description'].capitalize()
    elevation = int(gmaps.elevation((lat, lon))[0]['elevation'])

    out = f'🏙 Выбранный населенный пункт - <b>{params.city}</b>\n'
    out += ''
    out += f'🏔 высота - {elevation} м над уровнем моря\n'
    out += ''
    out += f'🌡 Температура воздуха {"+" if temp > 0 else "-" if temp < 0 else ""}{temp}\n'
    out += ''
    out += f"{wc.WEATHER_ICONS.get(weather['weather'][0]['main'], '')} {conditions}"
    if sun:
        d_rise = datetime.fromtimestamp(weather['sys']['sunrise'] + weather['timezone'] - config.timezone)
        d_set = datetime.fromtimestamp(weather['sys']['sunset'] + weather['timezone'] - config.timezone)
        out += f'\n🌥 облачность - {weather["clouds"]["all"]}%\n'
        out += f'🌬 скорость ветра - {weather["wind"]["speed"]} м/c\n'
        out += f'🌢 влажность воздуха - {weather["main"]["humidity"]}%\n'
        out += f'🫀 атмосферное давление - {int(weather["main"]["pressure"] * 0.750062)} мм рт.ст.\n'
        out += f'🌅 рассвет - {format_time(d_rise.hour)}:{format_time(d_rise.minute)}\n'
        out += f'🌇 закат - {format_time(d_set.hour)}:{format_time(d_set.minute)}\n'
        out += f'качество воздуха - {get_air_pollution(lat, lon)}'

    return out


def _get_forecast_data(view: str, params: WeatherHandler):
    url = 'https://api.openweathermap.org/data/2.5/onecall'
    lat, lon = get_location(params)
    exclude_view = 'current,minutely,hourly' if view == 'daily' else 'current,minutely,daily'
    weather_payload = {
        'lat': lat,
        'lon': lon,
        'appid': config.WEATHER_TOKEN,
        'units': 'metric',
        'lang': 'ru',
        'exclude': exclude_view,
    }
    data = requests.get(url, params=weather_payload).json()
    try:
        locale.setlocale(locale.LC_ALL, 'ru')
    except:
        pass
    return data


def weather_forecast(params: WeatherHandler):
    data = _get_forecast_data('daily', params)

    out = []

    for day in data['daily']:
        sunrise = datetime.fromtimestamp(day['sunrise'] + data['timezone_offset'] - config.timezone)
        sunset = datetime.fromtimestamp(day['sunset'] + data['timezone_offset'] - config.timezone)
        day_light = str(sunset - sunrise).split(':')
        s = f"<b><i>{datetime.fromtimestamp(day['dt']).strftime('%a, %d.%m')}</i></b>\n"
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


def hourly_forecast(params: WeatherHandler):
    data = _get_forecast_data('hourly', params)
    out = ''
    for hour in data['hourly'][:16:2]:
        out += f"<b><i>{datetime.fromtimestamp(hour['dt']).strftime('%a, %d.%m, %H:%M')}</i></b>\n"
        out += f'🌡 Температура воздуха {int(hour["temp"])}°\n'
        out += f'💁 По ощущениям {int(hour["feels_like"])}°\n'
        out += f"{wc.WEATHER_ICONS.get(hour['weather'][0]['main'], '')} {hour['weather'][0]['description']}\n"
        if hour.get('rain'):
            out += f'☔Ожидаемые осадки - {list(hour["rain"].values())[0]} мм\n'
        out += f'💧влажность воздуха - {hour["humidity"]}%\n'
        out += f'🌬 ветер {wc.WIND_DIRECTIONS[hour["wind_deg"] // 45]}, ' \
               f'скорость ветра - {int(hour["wind_speed"])} м/с,\n\n'
    return out


def is_rain(params=WeatherHandler('Kiev')):
    data = _get_forecast_data('hourly', params)
    rain = False
    long = 0
    mm = 0
    for index, item in enumerate(data):
        if index == 5 and not rain:
            return 'No rain in nearest 5 hours'
        if item.get('rain'):
            if not rain:
                hour = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                rain = True
            long += 1
            mm += list(item["rain"].values())[0]
        elif rain:
            return f'Внимание! в {hour} начнется дождь! Ожидается {mm} осадков и он продлится {long} часа(ов)'


# TODO: Create alert for rain. Beginning, end and quantity in MM. Check once per hour.

def get_rain_forecast(params: WeatherHandler):
    data = _get_forecast_data('hourly', params)
    for index, hour in enumerate(data['hourly'][:8]):
        if hour.get('rain'):
            count = 0
            quant = 0
            while data['hourly'][index + 1].get('rain'):
                count += 1
                quant += list(data['hourly'][index + 1]["rain"].values()[0])
                index += 1
