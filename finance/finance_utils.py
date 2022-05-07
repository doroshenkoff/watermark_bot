from bs4 import BeautifulSoup
import requests
from fake_headers import Headers
from .finance_constants import *


def currency_foreign():

    URL1 = 'https://query2.finance.yahoo.com/v7/finance/quote?formatted=true&crumb=AE8CmrGm.sp&lang=en-US&region=US&symbols='
    URL2 = '&fields=messageBoardId%2ClongName%2CshortName%2CmarketCap%2CunderlyingSymbol%2CunderlyingExchangeSymbol%2CheadSymbolAsString%2CregularMarketPrice%2CregularMarketChange%2CregularMarketChangePercent%2CregularMarketVolume%2Cuuid%2CregularMarketOpen%2CfiftyTwoWeekLow%2CfiftyTwoWeekHigh%2CtoCurrency%2CfromCurrency%2CtoExchange%2CfromExchange&corsDomain=finance.yahoo.com'
    header = Headers().generate()
    out = ''
    for fin in FINANCE_CONSTANTS:
        data = requests.get(f'{URL1}{fin.yahoo_code}{URL2}', headers=header).json()
        price = data["quoteResponse"]["result"][0]["regularMarketPrice"]
        price_open = data["quoteResponse"]["result"][0]["regularMarketOpen"]
        sym = '▼' if price['raw'] < price_open['raw'] else '▲'
        out += f'{fin.view} - {sym} {price["fmt"]}💲\n'
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
