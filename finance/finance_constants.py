from collections import namedtuple

Currency = namedtuple('Currency', 'name yahoo_code view')

FINANCE_CONSTANTS = [
    Currency('EUR', 'EURUSD=X', '€'),
    Currency('GBP', 'GBPUSD=X', '💷'),
    Currency('BTC', 'BTC-USD', '₿'),
    Currency('Gold', 'GC=F', 'Золото'),
    Currency('Oil', 'CL=F', '🛢 Нефть')
]