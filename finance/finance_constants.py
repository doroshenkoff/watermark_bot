from collections import namedtuple

Currency = namedtuple('Currency', 'name yahoo_code view')

FINANCE_CONSTANTS = [
    Currency('EUR', 'EURUSD=X', '€ Euro'),
    # Currency('GBP', 'GBPUSD=X', '💷 Pound'),
    Currency('BTC', 'BTC-USD', '₿ Bitcoin'),
    Currency('ETH', 'ETH-USD', '↕Ethereum'),
    Currency('Gold', 'GC=F', '🏆 Золото'),
    Currency('Oil', 'CL=F', '🛢 Нефть')
]
