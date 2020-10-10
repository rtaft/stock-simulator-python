import inspect
import importlib
import git
import os
import random
import sys
import shutil

from traders.interface import TraderInterface


def initiate_traders(simulator=None, traders=None, trader_locations=None):
    """
        :param trader_data: Dictionary of trader_ids to trader data params
    """
    trader_info = []
    if traders:
        print(traders)
        for trader in traders:
            if not isinstance(trader, dict):
                trader = dict(trader.__dict__)

            if trader.get('repo'):
                repo_traders = get_from_repo(trader.get('repo'), True)
                print(repo_traders)
                if repo_traders:
                    for repo_trader in repo_traders:
                        if (repo_trader.get('name') == trader.get('name')):
                            sys.path.append(repo_trader.get('repo'))
                            trader_info.append(dict(location=repo_trader.get('path').replace('/', '.')[:-3], trader_id=trader.get('trader_id')))
            elif trader.get('location'):
                if trader.get('location')[:7] == 'file://':
                    trader_info.append(dict(location='traders.{}'.format(trader.get('location')[7:-3]), trader_id=trader.get('trader_id')))
    if trader_locations:
        for trader_location in trader_locations:
            if trader_location[:7] == 'file://':
                trader_location = trader_location[7:]
            trader_info.append(dict(location='traders.{}'.format(trader_location[:-3]), trader_id=None))
    
    trader_instances = []
    for trader in trader_info:
        importlib.import_module(trader.get('location'))
        trader_module = get_class(trader.get('location'))
        for _, obj in inspect.getmembers(trader_module):
            if inspect.isclass(obj):
                if obj != TraderInterface:
                    for mro in inspect.getmro(obj):
                        if mro == TraderInterface:
                            trader_obj = obj(
                                simulator, trader_id=trader.get('trader_id'))
                            trader_instances.append(trader_obj)
    """
        if not isinstance(traders, list):
            traders = [traders]
        trader_instances = []
        for trader in traders:
            location = ''
            trader_id = 0
            if isinstance(trader, dict):
                location = trader['location']
            elif isinstance(trader, str):
                location = trader
            else:
                location = trader.location
                trader_id = trader.trader_id

            if location[:7] == 'file://':
                path = 'traders.{}'.format(location[7:-3])
                importlib.import_module(path)
                trader_module = get_class(path)
                for _, obj in inspect.getmembers(trader_module):
                    if inspect.isclass(obj):
                        if obj != TraderInterface:
                            for mro in inspect.getmro(obj):
                                if mro == TraderInterface:
                                    trader_obj = obj(
                                        simulator, trader_id=trader_id)
                                    trader_instances.append(trader_obj)
    """
    return trader_instances


def is_trader_instance(path):
    try:
        importlib.import_module(path)
    except Exception as e:
        return False
    trader_module = get_class(path)
    for _, obj in inspect.getmembers(trader_module):
        if inspect.isclass(obj):
            if obj != TraderInterface:
                for mro in inspect.getmro(obj):
                    if mro == TraderInterface:
                        trader_obj = obj(None)
                        return trader_obj.get_name()
    return False


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def get_from_repo(repo, persist=False):
    temp = 'tmp'
    pathname = '{}/repo{}'.format(temp, random.randint(100000, 1000000))
    if not os.path.exists(temp):
        os.mkdir(temp)
    os.mkdir(pathname)
    print("Download to {}".format(pathname))
    git.Git(pathname).clone(repo)
    #files = os.listdir(pathname)
    trader_files = []
    # for pathname in files:
    repo = pathname + '/' + os.listdir(pathname)[0]
    sys.path.append(repo)
    for root, _, files in os.walk(pathname, topdown=True):
        # print('root {}'.format(root))
        # print('files {}'.format(files))
        # print('?? {}'.format(_))

        # TODO ignore git path.
        for filename in files:
            if filename[-3:] == '.py':
                fullpath = os.path.join(root, filename)[len(repo)+1:]
                name = is_trader_instance(fullpath[:-3].replace('/', '.'))
                if name:
                    trader_files.append(
                        dict(path=fullpath, file=filename, name=name, repo=repo))
    sys.path.remove(repo)
    if not persist:
        shutil.rmtree(pathname)
        print('Removed {}'.format(pathname))
    return trader_files

    # TODO is there a requirements.txt file and if so load it.
    # TODO how to prevent mallicious software
