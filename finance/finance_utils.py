from bs4 import BeautifulSoup
import requests
from fake_headers import Headers
from datetime import date

import config
from .finance_constants import *


def currency_foreign(details=False):

    URL1 = 'https://query2.finance.yahoo.com/v7/finance/quote?formatted=true&crumb=AE8CmrGm.sp&lang=en-US&region=US&symbols='
    URL2 = '&fields=messageBoardId%2ClongName%2CshortName%2CmarketCap%2CunderlyingSymbol%2CunderlyingExchangeSymbol%2CheadSymbolAsString%2CregularMarketPrice%2CregularMarketChange%2CregularMarketChangePercent%2CregularMarketVolume%2Cuuid%2CregularMarketOpen%2CfiftyTwoWeekLow%2CfiftyTwoWeekHigh%2CtoCurrency%2CfromCurrency%2CtoExchange%2CfromExchange&corsDomain=finance.yahoo.com'
    header = Headers().generate()
    out = ''
    for fin in FINANCE_CONSTANTS:
        data = requests.get(f'{URL1}{fin.yahoo_code}{URL2}', headers=header).json()
        price = data["quoteResponse"]["result"][0]["regularMarketPrice"]
        price_open = data["quoteResponse"]["result"][0]["regularMarketOpen"]
        price_range = data["quoteResponse"]["result"][0]['regularMarketDayRange']['raw']
        percentage = data["quoteResponse"]["result"][0]['regularMarketChangePercent']['fmt']
        deviation = (price_open['raw'] - price['raw']) * 20 / price_open['raw']
        mark = '' if percentage[0] == '-' else '+'
        sym = '▼' * min(int(deviation) + 1, 5) if deviation > 0 else '▲' * -max(int(deviation) - 1, -5)
        if details:
            out += f'<b><i>{fin.view}</i></b>:\n<b>Current</b>: {sym} {price["fmt"]}💲\n' \
                   f'<b>Open</b>: {price_open["fmt"]}💲\n<b>Range</b>: {price_range}💲\n' \
                   f'<b>Deviation</b>: {mark}{percentage}\n\n'
        else:
            out += f'{fin.view} - {sym} {price["fmt"]}💲\n'
    return out


def get_spark_finance(period: int):
    url = 'https://yfapi.net/v8/finance/spark'
    header = {'x-api-key': config.YAHOO_API_KEY}
    yahoo_codes = ','.join(fin.yahoo_code for fin in FINANCE_CONSTANTS)
    params = {
                'interval': '1d',
                'range': '1mo',
                'symbols': yahoo_codes
            }

    data = requests.get(url, params=params, headers=header).json()
    out = ''
    for fin in FINANCE_CONSTANTS:
        spark = data[fin.yahoo_code]
        interval = min(len(spark['timestamp']), period)
        spark_dict = {date.fromtimestamp(k): v for k, v in
                      zip(spark['timestamp'][::-1][:interval], spark["close"][::-1][:interval])}
        spark_min = min(spark_dict, key=spark_dict.get)
        spark_max = max(spark_dict, key=spark_dict.get)
        min_date = min(spark_dict)
        max_date = max(spark_dict)
        out += f'<b><i>{fin.view}</i></b>:\n'
        out += f'Beginning: {min_date.strftime("%d-%m-%Y")} - <b>{spark_dict[min_date]}💲</b>\n'
        out += f'End: {max_date.strftime("%d-%m-%Y")} - <b>{spark_dict[max_date]}💲</b>\n'
        deviation = (spark_dict[max_date] - spark_dict[min_date]) / spark_dict[min_date] * 100
        mark = '' if deviation <= 0 else '+'
        sym = '▲' * min(int(deviation / 5) + 1, 5) if deviation > 0 else '▼' * -max(int(deviation / 5) - 1, -5)
        out += f'<b>Deviation</b>: {mark}{round(deviation, 2)}%    {sym}\n'
        out += f'Minimum: {spark_min.strftime("%d-%m-%Y")} - <b>{spark_dict[spark_min]}💲</b>\n'
        out += f'Maximum: {spark_max.strftime("%d-%m-%Y")} - <b>{spark_dict[spark_max]}💲</b>\n\n'
    return out



def get_nbu_cur():
    bs = BeautifulSoup(requests.get('https://minfin.com.ua/currency/nbu/').text, features="html.parser")
    tags = bs.find_all('p', {'class': 'sc-1mi6rpw-9 kdhvRG'})[:2]
    usd, eur = tags[0].text, tags[1].text
    out = 'Официальный курс НБУ'
    out += '\n'
    out = f'💲 USD - {usd} грн'
    out += '\n'
    out += f'€ EUR - {eur} грн'
    return out


if __name__ == '__main__':
    print(get_spark_finance(3))