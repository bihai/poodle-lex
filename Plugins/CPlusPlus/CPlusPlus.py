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

def create_emitter(lexical_analyzer, plugin_files_directory, output_directory, plugin_options):
    return CPlusPlusEmitter(lexical_analyzer, plugin_files_directory, output_directory, plugin_options)
    
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
        @param lexical_analyzer: DeterministicIR object representing the lexical analyzer to emit as FreeBasic code.
        @param depedencies: dict mapping string module identifiers of dependencies to Python module objects.
        @param plugin_options: LanguagePlugins.PluginOptions object containing options which affect the generation of code.
        """
        self.dfa_ir = dfa_ir
        
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
        
        self.class_name = plugin_options.class_name
        if self.class_name is None:
            self.class_name = self.default_class_name
        self.base_file_name = plugin_options.file_name
        if self.base_file_name is None:
            self.base_file_name = self.class_name
        self.namespace = plugin_options.namespace
        if self.namespace is None:
            self.namespace = CPlusPlusEmitter.default_namespace
      
    def get_files_to_copy(self):
        return []
        return [os.path.join(*i) for i in [
            ("demo", "demo.c"),
            ("demo", "make_demo.bat"),
            ("demo", "make_demo.sh")
        ]]

    def get_output_directories(self):
        return [os.path.join(*i) for i in [
            ("demo",)
        ]]
        
    def get_files_to_generate(self):
        files = [
            (self.h_file, self.plugin_options.file_name + ".h"),
            (self.cpp_file, self.plugin_options.file_name + ".cpp"),
            (self.demo_file, self.demo_file),
            (self.windows_makefile, self.windows_makefile),
            (self.linux_makefile, self.linux_makefile)
        ]
        if len(self.lexical_analyzer.sections) > 1:
            files.extend((
                (self.mode_bi_file, self.plugin_options.file_name + "ModeStack.bi"),
                (self.mode_bas_file, self.plugin_options.file_name + "ModeStack.bas")
            ))
        return files

      
      
      
    # Public interface
    def emit(self):
        """
        Emits the lexical analyzer as a C header file and source file.
        """
        if not self.lexical_analyzer.is_finalized():
            self.lexical_analyzer.finalize()
        self.dfa = self.lexical_analyzer.get_min_dfa()
        self.map_state_ids()
        self.map_rule_names()
        
        # Emit lexical analyzer header
        h_template_file = os.path.join(self.plugin_files_directory, CPlusPlusEmitter.h_file)
        h_output_file = os.path.join(self.output_directory, self.base_file_name + ".h")
        for stream, token, indent in FileTemplate(h_template_file, h_output_file):
            if token == 'ENUM_TOKEN_IDS':
                token_ids = [self.rule_ids[rule.id.upper()] for rule in self.lexical_analyzer.rules]
                token_ids.extend([self.rule_ids[id.upper()] for id in self.lexical_analyzer.reserved_ids])
                CPlusPlusEmitter.emit_enum_list(stream, indent, token_ids)
            elif token == "HEADER_GUARD":
                stream.write("%s_%s_H" % (self.namespace.upper(), self.base_file_name.upper()))
            else:
                self.process_common_tokens(token, stream, 'header file template')
        
        # Emit lexical analyzer source
        cpp_template_file = os.path.join(self.plugin_files_directory, CPlusPlusEmitter.cpp_file)
        cpp_output_file = os.path.join(self.output_directory, self.base_file_name + ".cpp")
        for stream, token, indent in FileTemplate(cpp_template_file, cpp_output_file):
            if token == 'ENUM_STATE_IDS':
                CPlusPlusEmitter.emit_enum_list(stream, indent, list(self.ids.values()))
            elif token == 'INITIAL_STATE':
                stream.write(self.ids[self.dfa.start_state].upper())
            elif token == 'INVALID_CHAR_STATE':
                stream.write('STATE_INVALIDCHAR')
            elif token == 'STATE_MACHINE':
                self.generate_state_machine(stream, indent)
            elif token == "TOKEN_IDNAMES_LIMIT":
                stream.write(str(len(self.rule_ids)+1))
            else:
                self.process_common_tokens(token, stream, 'source file template')
                
        # Emit demo files
        for support_file, description in [
            (CPlusPlusEmitter.demo_file, 'demo source template'),
            (CPlusPlusEmitter.windows_makefile, 'windows demo build script template'),
            (CPlusPlusEmitter.linux_makefile, 'linux demo build script template')
        ]:
            support_template_file = os.path.join(self.plugin_files_directory, support_file)
            support_output_file = os.path.join(self.output_directory, support_file)
            for stream, token, indent in FileTemplate(support_template_file, support_output_file):
                if token == "SELECT_ID_STRING":
                    rule_id_list = [rule.id for rule in self.lexical_analyzer.rules]
                    rule_id_list.extend(self.lexical_analyzer.reserved_ids)
                    for rule_id in rule_id_list:
                        indent_spaces = " "*indent
                        stream.write("%scase %s::Token::%s:\n" % (indent_spaces, self.class_name, self.rule_ids[rule_id.upper()]))
                        stream.write("%s    id_string = \"%s\";\n" % (indent_spaces, rule_id))
                        stream.write("%s    break;\n" % indent_spaces)
                else:
                    self.process_common_tokens(token, stream, description)

        
    def get_files_to_copy(self):
        return []
        return [os.path.join(*i) for i in [
            ("demo", "demo.c"),
            ("demo", "make_demo.bat"),
            ("demo", "make_demo.sh")
        ]]

    def process(self, token):
        if token.token == 'BASE_CLASS':
            if len(self.lexical_analyzer.sections) > 1:
                token.stream.write(self.formatter.get_mode_stack_class_name())
            else:



            
    @staticmethod
    def emit_enum_list(stream, indent, items):
        if len(items) == 0:
            return
        item_iter = iter(items)
        stream.write(' '*indent + next(item_iter))
        for item in item_iter:
            stream.write(',\n' + ' '*indent + item)
        stream.write('\n')
               
    # Private files
    def map_state_ids(self):
        """
        Maps all states to an enum element in the C source code.
        """
        self.ids[self.dfa.start_state] = "STATE_INITIALSTATE"
        self.ids[None] = "STATE_INVALIDCHAR"
        for state in self.dfa:
            if state != self.dfa.start_state:
                initial_id = "STATE_%s" % "_".join([i.upper() for i in sorted(list(state.ids))])
                id = initial_id[0:256]
                n = 1
                while id in self.ids.values() or id.lower() in CPlusPlusEmitter.reserved_keywords:
                    id = "%s%d" % (initial_id, n)
                    n += 1
                self.ids[state] = id
                
    def map_rule_names(self):
        """
        Maps all rule names to an enum element in the C source code
        """
        all_ids = [rule.id.upper() for rule in self.lexical_analyzer.rules]
        all_ids.extend([id.upper() for id in self.lexical_analyzer.reserved_ids])
        for id in all_ids:
            code_id = "%s" % id
            n = 1
            while code_id in self.rule_ids.values() or code_id.lower() in CPlusPlusEmitter.reserved_keywords:
                code_id = '%s%d' % (id, n)
                n += 1
            self.rule_ids[id] = code_id
        
    def generate_state_machine(self, stream, indent):
        """
        Generates a state machine in c source code represented by if blocks within a switch block.
        @param stream: a Python file object to which the state machine should be written
        @param indent: the number of spaces by which the code should be indented.
        """
        code = CodeEmitter(stream)
        for i in xrange(indent/4):
            code.indent()
        
        for i, state in enumerate(self.dfa):
            if i != 0:
                code.line()
            code.line("case %s:" % self.ids[state])
            code.indent()
            capture = False
            for rule in self.lexical_analyzer.rules:
                if rule.id in state.ids:
                    if rule.action is not None and rule.action.lower() == 'capture':
                        capture = True
            if (capture):
                code.line("capture = true;")
            
            def format_case(range):
                if range[0] == range[1]:
                    return "c == %d" % range[0]
                else:
                    return "(c >= %d && c <= %d)" % range

            if state == self.dfa.start_state:
                code.line("if (c == -1)")
                code.indent()
                code.line("return Token(Token::ENDOFSTREAM);")
                code.dedent()
                if_statement = "else if"
            else:
                if_statement = "if"
                    
            found_zero = False
            for destination, edges in state.edges.iteritems():
                code.line("%s (%s)" % (if_statement, " || ".join([format_case(i) for i in edges])))
                if if_statement == "if":
                    if_statement = "else if"
                code.indent()
                code.line("state = %s;" % self.ids[destination])
                code.dedent()
                
            # else case (return token if in final state
            if len(state.edges) > 0:
                code.line("else")
                code.indent()

            if len(state.final_ids) > 0:
                tokens_by_priority = [rule.id for rule in self.lexical_analyzer.rules]
                token = min(state.final_ids, key = lambda x: tokens_by_priority.index(x)).upper()
                rule = [rule for rule in self.lexical_analyzer.rules if rule.id.upper() == token][0]
                if rule.action is not None and rule.action.lower() == 'skip':
                    # Reset state machine if token is skipped
                    if len(state.edges) > 0:
                        code.dedent()
                        code.line("{")
                        code.indent()
                    code.line("state = %s;" % self.ids[self.dfa.start_state])
                    code.line("text.clear();")
                    code.line("continue;")
                    if len(state.edges) > 0:
                        code.dedent()
                        code.line("}")
                        code.indent()
                elif rule.action is not None and rule.action.lower() == 'capture':
                    code.line("return Token(Token::%s, text);" % self.rule_ids[token])
                else:
                    code.line("return Token(Token::%s);" % self.rule_ids[token])
            else:
                code.line("state = STATE_INVALIDCHAR;")
            if len(state.edges) > 0:
                code.dedent()

            code.line("break;")
            code.dedent()
            