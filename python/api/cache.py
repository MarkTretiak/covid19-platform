import time, functools

_store = {}

def cache(ttl=300):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = (fn.__name__, args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in _store and now - _store[key][0] < ttl:
                return _store[key][1]
            result = fn(*args, **kwargs)
            _store[key] = (now, result)
            return result
        return wrapper
    return decorator