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

class FreeBasic(object):
    """
    Emits a lexical analyzer as FreeBasic source code.
    @ivar lexical_analyzer: the lexical analyzer to emit
    @ivar ids: a dict mapping states to an enum element in the FreeBasic source
    @ivar dfa: the deterministic finite automata (DFA) representing the lexical analyzer.
    """
    template_dir = ('Template', 'FreeBasic')
    source_dir = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'Generator', 'Emitter')
    if getattr(sys, 'frozen', None) is None:
        source_dir = os.path.dirname(os.path.realpath(__file__))
    source_dir = os.path.join(source_dir, '..', '..', *template_dir)
    bi_template_file = os.path.join(source_dir, "LexicalAnalyzer.bi")
    bas_template_file = os.path.join(source_dir, "LexicalAnalyzer.bas")
    reserved_keywords = [
        'if', 'then', 'else', 'elseif', 'for', 'next', 'do', 'loop',
        'while', 'wend', 'goto', 'sub', 'function', 'end', 'type', 'is',
        'and', 'or', 'xor', 'not', 'goto', 'property', 'constructor', 'destructor',
        'namespace', 'string', 'integer', 'double', 'single', 'byte', 'ptr', 'any',
        'byref', 'byval', 'as', 'ubyte', 'short', 'ushort', 'uinteger', 'long',
        'ulong', 'longint', 'ulongint', 'cast', 'len', 'case', 'const', 'continue',
        'enum', 'extern', 'int', 'return', 'static', 'union', 'unsigned'
    ]
    
    def __init__(self, lexical_analyzer):
        """
        @param lexical_analyzer: the lexical analyzer to emit as FreeBasic code.
        """
        self.lexical_analyzer = lexical_analyzer
        self.ids = {}
        self.rule_ids = {}
        self.dfa = None
        
    def map_state_ids(self):
        """
        Maps all states to an enum element in the FreeBasic source code.
        """
        self.ids[self.dfa.start_state] = "InitialState"
        for state in self.dfa:
            if state != self.dfa.start_state:
                initial_id = "".join([i.title() for i in sorted(list(state.ids))])
                id = initial_id
                n = 1
                while id in self.ids.values() or id.lower() in FreeBasic.reserved_keywords:
                    id = "%s%d" % (initial_id, n)
                    n += 1
                self.ids[state] = id
                
    def map_rule_names(self):
        """
        Maps all rule names to an enum element in the FreeBasic source code
        """
        for rule in self.lexical_analyzer.rules:
            rule_id = rule.id.title()
            n = 1
            while rule_id in self.rule_ids.values() or rule_id.lower() in FreeBasic.reserved_keywords:
                rule_id = '%s%d' % (rule.id.title(), n)
                n += 1
            self.rule_ids[rule.id.title()] = rule_id
        
    def emit(self, header_file, source_file):
        """
        Emits the lexical analyzer as a FreeBasic header file and source file.
        @param header_file: the .bi file to which the header code should be emitted.
        @param source_file: the .bas file to which the source code should be emitted.
        """
        if not self.lexical_analyzer.is_finalized():
            self.lexical_analyzer.finalize()
        self.dfa = self.lexical_analyzer.get_min_dfa()
        self.map_state_ids()
        self.map_rule_names()
        
        # Emit lexical analyzer header
        for stream, token, indent in FileTemplate(FreeBasic.bi_template_file, header_file):
            if token == 'ENUM_TOKEN_IDS':
                for rule in self.lexical_analyzer.rules:
                    stream.write(" "*indent + self.rule_ids[rule.id.title()] + "\n")
            elif token == "TOKEN_IDNAMES_LIMIT":
                stream.write(str(len(self.lexical_analyzer.rules)+1))
            else:
                raise Exception('Unrecognized token in header template: "%s"' % token)
        
        # Emit lexical analyzer source
        for stream, token, indent in FileTemplate(FreeBasic.bas_template_file, source_file):
            if token == 'ENUM_STATE_IDS':
                for state_id in sorted(list(self.ids.values())):
                    stream.write(" "*indent + state_id + '\n')
            elif token == 'INITIAL_STATE':
                stream.write(self.ids[self.dfa.start_state])
            elif token == 'STATE_MACHINE':
                self.generate_state_machine(stream, indent)
            elif token == "TOKEN_IDNAMES_LIMIT":
                stream.write(str(len(self.lexical_analyzer.rules)+1))
            elif token == "TOKEN_IDNAMES":
                rule_id_list = [self.rule_ids[rule.id.title()] for rule in self.lexical_analyzer.rules]
                formatted_ids = ", _\n".join(" "*indent + "@\"%s\"" % rule_id for rule_id in rule_id_list)
                stream.write(formatted_ids + "_ \n")
            else:
                raise Exception('Unrecognized token in source template: "%s"' % token)
        
    def generate_state_machine(self, stream, indent):
        """
        Generates a state machine in FreeBasic source code represented by two tiers of "Select Case" statemenets.
        @param stream: a Python file object to which the state machine should be written
        @param indent: the number of spaces by which the code should be indented.
        """
        code = CodeEmitter(stream)
        for i in xrange(indent/4):
            code.indent()
        
        for i, state in enumerate(self.dfa):
            if i != 0:
                code.line()
            code.line("Case Poodle.%s" % self.ids[state])
            code.line("Select Case This.Character")
            code.indent()
            
            def ranges(i):
                for a, b in itertools.groupby(enumerate(i), lambda (x, y): y - x):
                    b = list(b)
                    yield b[0][1], b[-1][1]
            
            def format_case(range):
                if range[0] == range[1]:
                    return "%d" % range[0]
                else:
                    return "%d To %d" % range
            
            def emit_check_zero(invalid_otherwise):
                code.line("If Stream->IsEndOfStream() Then")
                code.indent()
                code.line("Return Poodle.Token(Poodle.Token.EndOfStream, Poodle.Unicode.Text())")
                code.dedent()
                if invalid_otherwise:
                    code.line("Else")
                    code.indent()
                    code.line("Return Poodle.Token(Poodle.Token.InvalidCharacter, Text)")
                    code.dedent()
                code.line("End If")
                
            found_zero = False
            for destination, edges in state.edges.iteritems():
                code.line("Case %s" % ", ".join([format_case(i) for i in edges]))
                if state == self.dfa.start_state:
                    if 0 in zip(*iter(edges))[0]:
                        # Since 0 could mean either end of stream or a binary zero, use IsEndOfStream() to determine
                        found_zero = True
                        emit_check_zero(invalid_otherwise=False)
                code.line("State = Poodle.%s" % self.ids[destination])
                code.line()
            
            if state == self.dfa.start_state and not found_zero:
                code.line("Case 0")
                emit_check_zero(invalid_otherwise=True)
                code.line()
            
            # else case (return token if in final state
            code.line("Case Else")
            if len(state.final_ids) > 0:
                tokens_by_priority = [rule.id for rule in self.lexical_analyzer.rules]
                token = min(state.final_ids, key = lambda x: tokens_by_priority.index(x)).title()
                code.line("Return Poodle.Token(Poodle.Token.%s, Text)" % self.rule_ids[token])
            else:
                code.line("Text.Append(This.Character)")
                code.line("This.Character = This.Stream->GetCharacter()")
                code.line("Return Poodle.Token(Poodle.Token.InvalidCharacter, Text)")
            
            code.dedent()
            code.line("End Select")
    
    output_dirs = [
        ("Demo",),
        ("Stream",),
        ("Stream", "Windows"),
        ("Stream", "Linux")
    ]
    files_to_copy = [
        ("Stream", "Windows", "MemoryMapWindows.bas"),
        ("Stream", "Windows", "MemoryMapWindows.bi"),
        ("Stream", "Linux", "MemoryMapLinux.bas"),
        ("Stream", "Linux", "MemoryMapLinux.bi"),
        ("Stream", "ASCIIStream.bas"),
        ("Stream", "ASCIIStream.bi"),
        ("Stream", "CharacterStream.bas"),
        ("Stream", "CharacterStream.bi"),
        ("Stream", "CharacterStreamFromFile.bas"),
        ("Stream", "CharacterStreamFromFile.bi"),
        ("Stream", "MemoryMap.bas"),
        ("Stream", "MemoryMap.bi"),
        ("Stream", "Unicode.bas"),
        ("Stream", "Unicode.bi"),
        ("Stream", "UnicodeConstants.bas"),
        ("Stream", "UnicodeConstants.bi"),
        ("Stream", "UTF8Stream.bas"),
        ("Stream", "UTF8Stream.bi"),
        ("Stream", "UTF16Stream.bas"),
        ("Stream", "UTF16Stream.bi"),
        ("Stream", "UTF32Stream.bas"),
        ("Stream", "UTF32Stream.bi"),
        ("Demo", "Demo.bas"),
        ("Demo", "make_demo.bat"),
        ("Demo", "make_demo.sh")
    ]
