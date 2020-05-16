import importlib
import pkgutil

import app_config
from api.restful import APP, SOCK
import pub
import eventlet 
eventlet.monkey_patch() 

def import_submodules(package):
    """ Import all submodules of a module, recursively, including subpackages
    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    print("Package {}".format(package))
    results = {}
    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = "{0}.{1}".format(package.__name__, name)
        print(full_name)
        results[full_name] = importlib.import_module(full_name)
        if is_pkg:
            results.update(import_submodules(full_name))
    return results


import_submodules(pub)

@SOCK.on('connect')
def connect():
    print('Websocket Connection')

if __name__ == "__main__":
    SOCK.run(APP, host='0.0.0.0', port=app_config.API_PORT, debug=False)
    #APP.run(host='0.0.0.0', port=app_config.API_PORT, debug=True, threaded=True)