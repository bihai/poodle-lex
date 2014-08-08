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

import os
import os.path
import re
import sys
import StringIO
import collections
import itertools
from EmitCode import CodeEmitter
from FileTemplate import FileTemplate
from PluginTemplate import PluginTemplate

def create_emitter(lexical_analyzer, dependencies, plugin_options):
    return CPlusPlusEmitter(lexical_analyzer, dependencies, plugin_options)
    
class CPlusPlusEmitter(PluginTemplate):
    """
    Emits a lexical analyzer as C++ source code.
    """
    reserved_keywords = [
        'auto', 'bool', 'break', 'case', 'char', 'class' 'const', 'continue', 'default', 'do',
        'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 
        'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
        'std', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while'
    ]
    h_file = "lexical_analyzer.h"
    cpp_file = "lexical_analyzer.cpp"
    demo_file = os.path.join('demo', 'demo.cpp')
    windows_makefile = os.path.join('demo', 'make_demo.bat')
    linux_makefile = os.path.join('demo', 'make_demo.sh')
    default_namespace = "Poodle"
    default_class_name = "LexicalAnalyzer"
    default_file_name = "LexicalAnalyzer"
    
    def __init__(self, dfa_ir, dependencies, plugin_options):
        """
        @param dfa_ir: DeterministicIR object representing the lexical analyzer to emit as FreeBasic code.
        @param depedencies: dict mapping string module identifiers of dependencies to Python module objects.
        @param plugin_options: LanguagePlugins.PluginOptions object containing options which affect the generation of code.
        """
        self.dfa_ir = dfa_ir
        self.plugin_options = plugin_options
        self.VariableFormatter = dependencies["VariableFormatter"].VariableFormatter
        self.StateMachineEmitter = dependencies["StateMachine"].StateMachineEmitter
        
        # Process plugin options
        for name, description in [
            (plugin_options.file_name, 'Base file name'),
            (plugin_options.namespace, 'Namespace')
        ]:
            if name is not None:
                if re.match("[A-Za-z_][A-Za-z0-9_]*", name) is None:
                    raise Exception("Invalid %s '%s'" % (description.lower(), name))
                elif name in CPlusPlusEmitter.reserved_keywords:
                    raise Exception("%s '%s' is reserved" % (description, name))
        
        if self.plugin_options.class_name is None:
            self.plugin_options.class_name = self.default_class_name
        if self.plugin_options.file_name is None:
            self.plugin_options.file_name = self.plugin_options.class_name
        if self.plugin_options.namespace is None:
            self.plugin_options.namespace = self.default_namespace
            
        self.formatter = self.VariableFormatter(plugin_options, self.reserved_keywords)
        self.class_name = self.plugin_options.class_name
        self.base_file_name = self.plugin_options.file_name
        self.namespace = self.plugin_options.namespace
      
    def get_files_to_copy(self):
        return []
        return [os.path.join(*i) for i in [
            ("demo", "make_demo.bat"),
            ("demo", "make_demo.sh")
        ]]

    def get_output_directories(self):
        return [os.path.join(*i) for i in [
            ("demo",)
        ]]
        
    def get_files_to_generate(self):
        return [
            (self.h_file, self.base_file_name + ".h"),
            (self.cpp_file, self.base_file_name + ".cpp"),
            (self.demo_file, self.demo_file),
            (self.windows_makefile, self.windows_makefile),
            (self.linux_makefile, self.linux_makefile)
        ]

    def process(self, token):
        if token.token == 'BASE_FILE_NAME':
            token.stream.write(self.base_file_name)
        elif token.token == 'CLASS_NAME':
            token.stream.write(self.class_name)
        elif token.token == 'ENUM_TOKEN_IDS':
            ids = sorted(rule for rule in self.dfa_ir.rule_ids.values() if rule is not None)
            ids.insert(0, 'invalidcharacter')
            ids.insert(0, 'endofstream')
            ids.insert(0, 'skippedtoken')
            for i, id in enumerate(ids):
                id_key = self.formatter.get_token_id(id)
                if i != len(ids)-1:
                    token.stream.write('{indent}{id},\n'.format(indent=' '*token.indent, id=id_key))
                else:
                    token.stream.write('{indent}{id}\n'.format(indent=' '*token.indent, id=id_key))
        elif token.token == 'ENUM_SECTION_IDS':
            code = CodeEmitter(token.stream, token.indent)
            code.line()
            if len(self.dfa_ir.sections) > 1:
                code.line('enum Mode');
                with code.block('{', '};'):
                    ids = sorted(self.dfa_ir.sections)
                    for i, id in enumerate(ids):
                        formatted = self.formatter.get_section_id(id)
                        if i == len(ids)-1:
                            code.line(formatted)
                        else:
                            code.line('{id},'.format(id=formatted))
                code.line()
        elif token.token == 'HEADER_GUARD':
            token.stream.write("{namespace}_{basefile}_H".format(
                namespace=self.namespace.replace(':', ''),
                basefile=self.base_file_name.upper()))
        elif token.token == 'INCLUDES':
            token.stream.write("{indent}#include \"{file_name}.h\"".format(
                indent=' '*token.indent,
                file_name=self.base_file_name))
        elif token.token == 'MODE_STACK_DECLARATION':
            token.stream.write('{indent}std::istream* stream;\n'.format(indent=' '*token.indent))
            if len(self.dfa_ir.sections) > 1:
                token.stream.write('{indent}{stack_type} mode;\n'.format(
                    indent=' '*token.indent,
                    stack_type=self.formatter.get_type('mode_stack', is_relative=True)))
        elif token.token == 'MODE_STACK_INCLUDE':
            if len(self.dfa_ir.sections) > 1:
                token.stream.write('#include <stack>\n\n')
        elif token.token == 'NAMESPACE':
            token.stream.write(self.namespace)
        elif token.token == 'PUSH_INITIAL_MODE':
            if len(self.dfa_ir.sections) > 1:
                token.stream.write('{indent}this->mode.push({initial_mode});\n'.format(
                    indent = ' '*token.indent,
                    initial_mode = self.formatter.get_section_id('::main::')))
        elif token.token == 'SELECT_ID_STRING':
            ids = sorted(rule for rule in self.dfa_ir.rule_ids.values() if rule is not None)
            code = CodeEmitter(token.stream, token.indent)
            for id in ids:
                with code.block('case {class_name}::Token::{token_id}:'.format(   
                    class_name=self.class_name,
                    token_id=self.formatter.get_token_id(id))):
                    code.line('id_string = "{id}";'.format(id=id))
                    code.line('break;')
        
        elif token.token == 'STATE_MACHINE_METHOD_DECLARATIONS':
            token.stream.write("{indent}{token_type} get_token();\n".format(
                indent = ' '*token.indent,
                token_type = self.formatter.get_type('token', is_relative=True)))
            if len(self.dfa_ir.sections) > 1:
                for section_id in self.dfa_ir.sections:
                    token.stream.write("{indent}{token_type} {method_name}();\n".format(
                        indent = ' '*token.indent,
                        token_type = self.formatter.get_type('token', is_relative=True),
                        method_name = self.formatter.get_state_machine_method_name(section_id, is_relative=True)))
        elif token.token == 'STATE_MACHINES':
            code = CodeEmitter(token.stream, token.indent)
            if len(self.dfa_ir.sections) > 1:
                self.emit_state_machine_switch(code)
            for section in self.dfa_ir.sections:
                state_machine_emitter = self.StateMachineEmitter(self.dfa_ir, section, self.formatter, code)
                state_machine_emitter.emit_state_machine()
        else:
            raise Exception("Unrecognized token: {0}".format(token.token))

    def emit_state_machine_switch(self, code):
        code.line('{token_type} {class_name}::get_token()'.format(
            token_type = self.formatter.get_type('token', is_relative=False),
            class_name = self.class_name))

        with code.block('{', '}'):
            code.line('{token_type} token;'.format(token_type=self.formatter.get_type('token', is_relative=False)))
            code.line("do")
            with code.block('{', '}} while(token.id == Token::{id});'.format(id=self.formatter.get_token_id('skippedtoken'))):
                code.line('switch(mode.top())')
                with code.block('{', '}'):
                    for section in sorted(i for i in self.dfa_ir.sections if i != '::main::'):
                        with code.block('case {mode_id}:'.format(mode_id = self.formatter.get_section_id(section))):
                            code.line('token = {method_name}();'.format(
                                method_name = self.formatter.get_state_machine_method_name(section, is_relative=True)))
                            code.line('break;')
                    
                    with code.block('default:'):
                        code.line('token = {method_name}();'.format(
                            method_name = self.formatter.get_state_machine_method_name('::main::', is_relative=True)))
            code.line('return token;')
                        
                    
