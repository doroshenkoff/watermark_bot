from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

from datetime import datetime
import googlemaps
import config
from collections import namedtuple

gmaps = googlemaps.Client(config.GOOGLE_API_KEY)

HOUSES = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII',
          8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}


HoroscopeItems = namedtuple('HoroscopeItems', 'name flatlib_name display')

HOROSCOPE_ITEMS = [
    HoroscopeItems('sun', const.SUN, '☉ Солнце'),
    HoroscopeItems('moon', const.MOON, '🌙 Луна'),
    HoroscopeItems('mercury', const.MERCURY, '☿ Меркурий'),
    HoroscopeItems('venus', const.VENUS, '♀ Венера'),
    HoroscopeItems('mars', const.MARS, '♂ Марс'),
    HoroscopeItems('jupiter', const.JUPITER, '♃ Юпитер'),
    HoroscopeItems('saturn', const.SATURN, '♄ Сатурн'),
    HoroscopeItems('asc', const.ASC, 'ASC Асцендент'),
    HoroscopeItems('mc', const.MC, 'MC Medium Coeli')
]

ZODIAC_ITEMS = {
    'Aries': '♈ Овен',
    'Taurus': '♉ Телец',
    'Gemini': '♊ Близнецы',
    'Cancer': '♋ Рак',
    'Leo': '♌ Лев',
    'Virgo': '♍ Дева',
    'Libra': '♎ Весы',
    'Scorpio': '♏ Скорион',
    'Sagittarius': '♐ Стрелец',
    'Capricorn': '♑ Козерог',
    'Aquarius': '♒ Водолей',
    'Pisces': '♓ Рыбы'
}


def get_horoscope(position='Киев'):
    loc = gmaps.geocode(position)[0]['geometry']['location']
    now = datetime.now()
    date_params = now.strftime("%Y/%m/%d"), now.strftime("%H:%M"), '+03:00'

    chart = Chart(Datetime(*date_params), GeoPos(*loc.values()))
    houses = [(house.id.replace('House', ''), house.lon) for house in chart.houses]
    houses.sort(key=lambda h: h[1])
    out = ''
    for item in HOROSCOPE_ITEMS:
        planet = chart.get(item.flatlib_name)

        for i, h in enumerate(houses):
            try:
                if planet.lon < h[1]:
                    house = int(houses[i - 1][0])
                    break
            except:
                house = 1
                break
        else:
            house = int(houses[-1][0])

        details = str(planet).split(' ')
        pos = details[2].split(":")
        out += f"{item.display}:  {ZODIAC_ITEMS.get(details[1], details[1])} {pos[0][1:]}°{pos[1]}, " \
               f"<b>{HOUSES[house]} дом</b>"
        if item.name == 'moon' and 195 <= planet.lon <= 225:
            out += " <b>💀Via Combusta💀</b>\n"
        else:
            out += "\n"
    return out


def is_via_combusta():
    now = datetime.now()
    date_params = now.strftime("%Y/%m/%d"), now.strftime("%H:%M"), '+03:00'
    chart = Chart(Datetime(*date_params), GeoPos('59n42', '30w65'))
    moon = chart.get(const.MOON)
    return 195 <= moon.lon <= 225



if __name__ == '__main__':
    print(get_horoscope())

