'''
全局变量
'''

def _init():
    global _global_map
    _global_map = {}

def getValue(key, defaultValue = None):
    try:
        return _global_map[key]
    except KeyError:
        return defaultValue

def setValue(key, value):
    _global_map[key] = value