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
import unicodedata

class StateIdFormatter(object):
    def __init__(self, rules, reserved_ids):
        def state_id_formatter(state):
            state_id = ''
            for rule in self.rules:
                if rule.id in state.ids:    
                    state_id += rule.name if rule.name is not None else 'Anonymous'
            return state_id
        self.cache = CachedFormatter(limit=64, reserved=reserved_ids)
        self.cache.add_cache('state_id', state_id_formatter)
        self.rules = rules
        for attr in dir(self.cache):
            if any(attr.startswith(i) for i in ('get_', 'add_', 'clear_')):
                setattr(self, attr, getattr(self.cache, attr))

class VariableFormatter(object):
    def __init__(self, plugin_options, reserved_ids, poodle_namespace):
        def section_id_formatter(section_id):
            path = section_id.split('.') if section_id is not None else None
            path = [i.replace(':', '') for i in path] if path is not None else None
            return ''.join(path[1:]) if section_id is not None and len(path) > 0 else ''
        def token_id_formatter(id):
            return id
            
        self.poodle_namespace = poodle_namespace
        self.plugin_options = plugin_options
        self.reserved_ids = reserved_ids
        self.cache = CachedFormatter(limit=64, reserved=reserved_ids)
        self.cache.add_cache('section_id', section_id_formatter, cache_name='section_and_tokens')
        self.cache.add_cache('token_id', token_id_formatter, cache_name='section_and_tokens')
        self.cache.add_section_id(None, '')
        self.cache.add_section_id('::main::', 'Main')
        for attr in dir(self.cache):
            if any(attr.startswith(i) for i in ('get_', 'add_', 'clear_')):
                setattr(self, attr, getattr(self.cache, attr))

    def get_class_name(self):
        return self.plugin_options.class_name

    def get_default_encoding(self):
        return self.get_scoped('Unicode.DefaultStringEncoding', is_relative=True, is_custom_namespace=False)
        
    def get_mode_stack_class_name(self):
        return self.get_class_name() + "Mode"
        
    def get_namespace(self):
        return self.plugin_options.namespace

    def get_scoped(self, id, is_relative, is_custom_namespace):
        if is_relative:
            if not is_custom_namespace and self.plugin_options.namespace != self.poodle_namespace:
                return '{poodle}.{type}'.format(poodle=self.poodle_namespace, type=type_text)
            else:
                return id
        else:
            return '{namespace}.{type}'.format(namespace=self.plugin_options.namespace, type=id)

    def get_state_machine_method_name(self, section, is_relative):
        method_name = 'GetToken{id}'.format(id=self.cache.get_section_id(section))
        if not is_relative:
            method_name = '{class_name}.{method_name}'.format(
                class_name=self.get_class_name(),
                method_name=method_name)
        return self.get_scoped(method_name, is_relative, is_custom_namespace=True)
            
    def get_type(self, type_name, is_relative):
        if type_name == 'mode':
            is_custom_namespace = True
            type_text = "{class_name}.ModeId".format(class_name=self.get_mode_stack_class_name())
        elif type_name == 'token':
            is_custom_namespace = True
            type_text = "{class_name}Token".format(class_name=self.plugin_options.class_name)
        elif type_name == 'text':
            is_custom_namespace = False
            type_text = 'Unicode.Text'
        elif type_name == 'encoding':
            is_custom_namespace = False
            type_text = 'Unicode.StringEncoding'
        elif type_name == 'character':
            is_custom_namespace = False
            type_text = 'Unicode.Codepoint'
        elif type_name == 'stream':
            is_custom_namespace = False
            type_text = 'CharacterStream'
        else:
            raise Exception("unrecognized type '{id}'".format(id=type_name))
        return self.get_scoped(type_text, is_relative, is_custom_namespace)

    def get_state_id_formatter(self, rules):
        return StateIdFormatter(rules, self.reserved_ids)
        
    def get_unicode_char_name(self, codepoint):
        try:
            unicode_name = unicodedata.name(unichr(codepoint)).replace(' ', '_').replace('-', '_')
            return "{namespace}_UCS_{name}".format(
                namespace = self.get_namespace().upper(),
                name = unicode_name.upper())
        except ValueError:
            return "&h%02x" % codepoint
