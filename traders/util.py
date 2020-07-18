import inspect, importlib

from database.trader import get_traders
from traders.interface import TraderInterface

def initiate_traders(simulator, traders):
    """
        :param trader_data: Dictionary of trader_ids to trader data params
    """
    if not isinstance(traders, list):
        traders = [traders]
    trader_instances = []
    for trader in traders:
        if trader.location[:7] == 'file://':
            path = 'traders.{}'.format(trader.location[7:-3])
            importlib.import_module(path)
            trader_module = get_class(path)
            for _, obj in inspect.getmembers(trader_module):
                if inspect.isclass(obj):
                    if obj != TraderInterface:
                        for mro in inspect.getmro(obj):
                            if mro == TraderInterface:
                                trader = obj(simulator, trader_id=trader.trader_id)
                                trader_instances.append(trader)
    return trader_instances

def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m