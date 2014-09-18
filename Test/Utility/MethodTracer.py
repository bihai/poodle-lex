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
import sys

def MethodTracer(cls):
    class DebugInitializer(object):
        def decorate(self, method_name, method):
            decorator = self
            def decorated_method(self, *args, **kw_args):
                args_text = [repr(i) for i in args]
                args_text.extend(["'{0}': {1}".format(k, repr(v)) for k, v in kw_args])
                print("{0}Entering {1}({2})".format(' '*decorator.count, method_name, ', '.join(args_text)))
                decorator.count += 1
                results = method.__get__(self, cls)(*args, **kw_args)
                decorator.count -= 1
                print("{0}Exiting {1} = {2}".format(' '*decorator.count, method_name, repr(results)))
                return results
            return decorated_method
    
        def __init__(self, *args, **kw_args):
            self.count = 0
            self.instance = cls(*args, **kw_args)
            for method_name, method in cls.__dict__.items():
                if callable(method):
                    new_method = self.decorate.__get__(self, DebugInitializer)(method_name, method).__get__(self.instance, cls)
                    setattr(self.instance, method_name, new_method)
                    setattr(self, method_name, new_method)
        
    return DebugInitializer
    