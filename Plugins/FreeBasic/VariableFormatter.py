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

from CachedFormatter import CachedFormatter

class VariableFormatter(object):
    def __init__(self, plugin_options):
        def token_method_formatter(section_id):
            return ''.join(i.title() for i in section_id[1:]) if section_id is not None and len(section_id) > 0 else ''
        def state_id_formatter(state):
            return "State" + "".join([i.title() for i in sorted(list(state.ids))])   
        self.plugin_options = plugin_options
        self.cache = CachedFormatter(limit=64)
        self.cache.add_cache('token_method_name', token_method_formatter)
        self.cache.add_cache('state_id', state_id_formatter)
        self.cache.add_token_method_name(None, '')
        self.cache.add_token_method_name(('::main::'), 'Main')
    
    def token_type(self):
        return "{namespace}.{class_name}Token".format(
            namespace=self.plugin_options.namespace,
            class_name=self.plugin_options.class_name)
    
    def section_type(self):
        return "{namespace}.{class_name}Section".format(
            namespace=self.plugin_options.namespace,
            class_name=self.plugin_options.class_name)
            
    def get_token_method_name(self, section):
        return self.cache.get_token_method_name(section)
    
    def get_state_id(self, state):
        self.cache.get_state_id(section)
        