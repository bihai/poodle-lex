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
    def __init__(self, plugin_options, reserved_ids):
        def section_id_formatter(section_id):
            path = section_id.split('.') if section_id is not None else None
            path = [i.upper().replace(':', '') for i in path] if path is not None else None
            return '_'.join(path[1:]) if section_id is not None and len(path) > 0 else ''
        def state_id_formatter(state):
            return '_'.join([i.upper() if i is not None else 'ANONYMOUS' for i in sorted(state.ids)])
        def token_id_formatter(id):
            return id.upper() if id is not None else None
            
        self.plugin_options = plugin_options
        self.cache = CachedFormatter(limit=64, reserved=reserved_ids)
        self.cache.add_cache('section_id', section_id_formatter, cache_name='section_and_tokens')
        self.cache.add_cache('token_id', token_id_formatter, cache_name='section_and_tokens')
        self.cache.add_cache('state_id', state_id_formatter)
        self.cache.add_token_id(None, 'ANONYMOUS')
        self.cache.add_token_id('endofstream', 'ENDOFSTREAM')
        self.cache.add_token_id('invalidcharacter', 'INVALIDCHARACTER')
        self.cache.add_section_id(None, '')
        self.cache.add_section_id('::main::', 'MAIN')
        self.cache.add_state_id('invalid_char_state', 'INVALID_CHAR_STATE')
        for attr in dir(self.cache):
            if any(attr.startswith(i) for i in ('get_', 'add_', 'clear_')):
                setattr(self, attr, getattr(self.cache, attr))

    def get_class_name(self):
        return self.plugin_options.class_name

    def get_scoped(self, id, is_relative):
        if is_relative:
            return id
        else:
            return '{class_name}::{type}'.format(class_name=self.get_class_name(), type=id)

    def get_state_machine_method_name(self, section, is_relative):
        section_id = self.cache.get_section_id(section).lower()
        if section_id != '':
            section_id = '_' + section_id
        method_name = 'get_token{id}'.format(id=section_id)
        return self.get_scoped(method_name, is_relative)
            
    def get_type(self, type_name, is_relative):
        if type_name == 'mode_stack':
            return "std::stack<{mode_type}>".format(mode_type=self.get_type('mode', is_relative))
        elif type_name == 'mode':
            type_text = 'Mode'
        elif type_name == 'token':
            type_text = 'Token'
        elif type_name == 'state':
            return 'State'
        else:
            raise Exception("unrecognized type '{id}'".format(id=type_name))
        return self.get_scoped(type_text, is_relative)
