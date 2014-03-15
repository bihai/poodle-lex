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

class LanguageEmitter(PluginTemplate):
    """
    Emits a lexical analyzer as FreeBasic source code.
    @ivar lexical_analyzer: the lexical analyzer to emit
    @ivar ids: a dict mapping states to an enum element in the FreeBasic source
    @ivar dfa: the deterministic finite automata (DFA) representing the lexical analyzer.
    """
    reserved_keywords = [
        'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
        'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 
        'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
        'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while'
    ]
    h_file = "lexical_analyzer.h"
    c_file = "lexical_analyzer.c"
    
    def __init__(self, lexical_analyzer, plugin_files_directory, output_directory):
        """
        @param lexical_analyzer: LexicalAnalyzer object representing the lexical analyzer to emit as FreeBasic code.
        @param plugin_files_directory: string specifying the location of template files
        @param output_directory: string specifying the directory where output files should be emitted
        """
        self.lexical_analyzer = lexical_analyzer
        self.plugin_files_directory = plugin_files_directory
        self.output_directory = output_directory
        self.ids = {}
        self.rule_ids = {}
        self.dfa = None
    
    # Public interface
    def emit(self):
        """
        Emits the lexical analyzer as a FreeBasic header file and source file.
        """
        if not self.lexical_analyzer.is_finalized():
            self.lexical_analyzer.finalize()
        self.dfa = self.lexical_analyzer.get_min_dfa()
        self.map_state_ids()
        self.map_rule_names()
        
        # Emit lexical analyzer header
        h_template_file = os.path.join(self.plugin_files_directory, LanguageEmitter.h_file)
        h_output_file = os.path.join(self.output_directory, LanguageEmitter.h_file)
        for stream, token, indent in FileTemplate(h_template_file, h_output_file):
            if token == 'ENUM_TOKEN_IDS':
                token_ids = [self.rule_ids[rule.id.upper()] for rule in self.lexical_analyzer.rules]
                token_ids.append("PTKN_TOKENIDCOUNT")
                LanguageEmitter.emit_enum_list(stream, indent, token_ids)
            elif token == "TOKEN_IDNAMES_LIMIT":
                stream.write(str(len(self.lexical_analyzer.rules)+1))
            else:
                raise Exception('Unrecognized token in header template: "%s"' % token)
        
        # Emit lexical analyzer source
        c_template_file = os.path.join(self.plugin_files_directory, LanguageEmitter.c_file)
        c_output_file = os.path.join(self.output_directory, LanguageEmitter.c_file)
        for stream, token, indent in FileTemplate(c_template_file, c_output_file):
            if token == 'ENUM_STATE_IDS':
                LanguageEmitter.emit_enum_list(stream, indent, list(self.ids.values()))
            elif token == 'INITIAL_STATE':
                stream.write(self.ids[self.dfa.start_state].upper())
            elif token == 'STATE_MACHINE':
                self.generate_state_machine(stream, indent)
            elif token == "TOKEN_IDNAMES":
                rule_id_list = [rule.id for rule in self.lexical_analyzer.rules]
                formatted_ids = ", \n".join(" "*indent + "\"%s\"" % rule_id for rule_id in rule_id_list)
                stream.write(formatted_ids + " \n")
            elif token == "CAPTURE_CASES":
                for id in [rule.id for rule in self.lexical_analyzer.rules if rule.action is not None and rule.action.lower() == "capture"]:
                    stream.write(' '*indent + "case %s:\n" % self.rule_ids[id.upper()])
            else:
                raise Exception('Unrecognized token in source template: "%s"' % token)

    def get_output_directories(self):
        return [os.path.join(*i) for i in [
            ("demo",)
        ]]
        
    def get_files_to_copy(self):
        return [os.path.join(*i) for i in [
            ("demo", "demo.c"),
            ("demo", "make_demo.bat"),
            ("demo", "make_demo.sh")
        ]]
    
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
        Maps all states to an enum element in the FreeBasic source code.
        """
        self.ids[self.dfa.start_state] = "PLA_STATE_INITIALSTATE"
        for state in self.dfa:
            if state != self.dfa.start_state:
                initial_id = "PLA_STATE_" + "_".join([i.upper() for i in sorted(list(state.ids))])
                id = initial_id[0:256]
                n = 1
                while id in self.ids.values() or id.lower() in LanguageEmitter.reserved_keywords:
                    id = "%s%d" % (initial_id, n)
                    n += 1
                self.ids[state] = id
                
    def map_rule_names(self):
        """
        Maps all rule names to an enum element in the FreeBasic source code
        """
        for rule in self.lexical_analyzer.rules:
            rule_id = "PTKN_" + rule.id.upper()
            n = 1
            while rule_id in self.rule_ids.values() or rule_id.lower() in LanguageEmitter.reserved_keywords:
                rule_id = '%s%d' % ("PTKN_" + rule.id.upper(), n)
                n += 1
            self.rule_ids[rule.id.upper()] = rule_id
        
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
            
            def ranges(i):
                for a, b in itertools.groupby(enumerate(i), lambda (x, y): y - x):
                    b = list(b)
                    yield b[0][1], b[-1][1]
            
            def format_case(range):
                if range[0] == range[1]:
                    return "c == %d" % range[0]
                else:
                    return "(c >= %d && c <= %d)" % range

            if state == self.dfa.start_state:
                code.line("if (feof(f))")
                code.line("{")
                code.indent()
                code.line("token.id = PTKN_ENDOFSTREAM;")
                code.line("done = 1;")
                code.dedent()
                code.line("}")
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
                code.line("{")
                code.indent()

            if len(state.final_ids) > 0:
                tokens_by_priority = [rule.id for rule in self.lexical_analyzer.rules]
                token = min(state.final_ids, key = lambda x: tokens_by_priority.index(x)).upper()
                rule = [rule for rule in self.lexical_analyzer.rules if rule.id.upper() == token][0]
                if rule.action is not None and rule.action.lower() == 'skip':
                    # Reset state machine if token is skipped
                    code.line("state = %s;" % self.ids[self.dfa.start_state])
                    code.line("ungetc(c, f);")
                    code.line("token_index = 0;")
                else:
                    code.line("token.id = %s;" % self.rule_ids[token])
                    code.line("done = 1;")
            else:
                code.line("token.id = PTKN_INVALIDCHARACTER;")
                code.line("done = 1;")

            if len(state.edges) > 0:
                code.dedent()
                code.line("}")
            code.line("break;")
            code.dedent()
            