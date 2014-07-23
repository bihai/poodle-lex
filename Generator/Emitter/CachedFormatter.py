# Copyright (C) 2014 Parker Michaels
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

class CachedFormatter(object):
    class ValueCache(object):
        def __init__(self):
            self.keys = {}
            self.values = set()

    """
    Utility class for maintaining a list of names mapped to objects. Duplicate
    names are suffixed with a number.
    """
    def __init__(self, limit=64, reserved=[]):
        """
        @param limit: the maximum length of a formatted name
        """
        self.limit = limit
        self.caches = {}
        self.reserved = set([i.lower() for i in reserved])
        
    def insert(self, cache, key, value, formatter=None):
        """
        Inserts maps an object to a name, and modifies the name until the 
        cache has space.
        @param cache: dict mapping an object to a string name which serves as a cache
        @param key: object which is to be mapped to a value
        @param value: string representing the name which the object should map to
        """
        if key in cache.keys:
            return cache.keys[key]
        if formatter is not None:
            value = formatter(key)
        n = 1
        candidate = value[:self.limit]
        while candidate.lower() in cache.values or candidate.lower() in self.reserved:
            suffix = str(n)
            prefix = value[:self.limit-len(suffix)]
            candidate = prefix + suffix
            n += 1
        cache.keys[key] = candidate
        cache.values.add(candidate.lower())
        return candidate
    
    def add_cache(self, name, formatter, cache_name=None): 
        """
        Adds a cache for a given formatter, and creates a 'get_xxx' method
        based on the name. Also creates a helper "add_xxx" method based on
        the name to fill the cache with predefined values.
        @param name: string containing the name of the cache to create
        @param formatter: function which creates a name given an object
        """
        if cache_name is None:
            cache_name = name
        if cache_name not in self.caches:
            cache = self.caches[cache_name] = CachedFormatter.ValueCache()
        else:
            cache = self.caches[cache_name]
        def get_value(param):
            return self.insert(cache, param, None, formatter)
        def add_value(key, value):
            self.insert(cache, key, value)
        def clear():
            cache.keys = {}
            cache.values = set()
        setattr(self, 'get_' + name, get_value)
        setattr(self, 'add_' + name, add_value)
        setattr(self, 'clear_' + name + 's', clear)
        