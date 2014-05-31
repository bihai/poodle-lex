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
        self.reserved = set(reserved)
        
    def insert(self, cache, key, value):
        """
        Inserts maps an object to a name, and modifies the name until the 
        cache has space.
        @param cache: dict mapping an object to a string name which serves as a cache
        @param key: object which is to be mapped to a value
        @param value: string representing the name which the object should map to
        """
        if key in cache:
            return key
        n = 2
        candidate = value[:self.limit]
        while candidate in cache.values() or candidate in self.reserved:
            prefix = str(n)
            suffix = value[:self.limit-len(prefix)]
            candidate = prefix + suffix
            n += 1
        cache[key] = candidate
        return candidate
    
    def add_cache(self, name, formatter): 
        """
        Adds a cache for a given formatter, and creates a 'get_xxx' method
        based on the name. Also creates a helper "add_xxx" method based on
        the name to fill the cache with predefined values.
        @param name: string containing the name of the cache to create
        @param formatter: function which creates a name given an object
        """
        if name not in self.caches:
            cache = self.caches[name] = {}
        else:
            cache = self.caches[name]
        def get_value(param):
            return self.insert(cache, param, formatter(param))
        def add_value(key, value):
            self.insert(cache, key, value)
        setattr(self, 'get_' + name, staticmethod(get_value))
        setattr(self, 'add_' + name, staticmethod(add_value))
        