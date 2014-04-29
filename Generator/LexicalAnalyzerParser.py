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

import LexicalAnalyzerAST
from LexicalAnalyzerLexer import LexicalAnalyzerParserException, LexicalAnalyzerLexer

class LexicalAnalyzerParser(object):
    def __init__(self, file, encoding):
        self.lexer = LexicalAnalyzerLexer(file, encoding)
        for NodeType in [
            LexicalAnalyzerAST.Rule,
            LexicalAnalyzerAST.Define,
            LexicalAnalyzerAST.ReservedId,
            LexicalAnalyzerAST.Pattern,
            LexicalAnalyzerAST.Section,
            LexicalAnalyzerAST.SectionReference
        ]:
            setattr(self, NodeType.__name__, self.create_line_wrapper(NodeType))
        self.rules_file = [self.Section('::main::')]
        
    def create_line_wrapper(self, NodeType):
        """
        Uses reflection to create a version of each task with the line 
        number of the rules file lexer bound to the constructor
        @param NodeType: a Python class to wrap
        """
        parent_self = self
        class Wrapper(NodeType):
            def __init__(self, *args):
                NodeType.__init__(self, *args, line_number=parent_self.lexer.line)
        return Wrapper
        
    def parse(self):
        """
        Parse the rules file into an AST tree
        @return: a Section object described by the rules file
        """
        self.lexer.skip('whitespace', 'comment', 'newline')
        while self.lexer.token != 'end of stream':
            self.parse_statement()
            self.lexer.skip('whitespace', 'comment', 'newline')
            
        return self.rules_file.pop()
        
    def parse_statement(self):
        """
        Parse parse a single statement in the rules file, and attach it
        to the LexicalAnalyzer object
        @return: None
        """
        name_or_action = self.lexer.expect('identifier')
        self.lexer.skip('whitespace')
        token, text = self.lexer.expect_one_of('colon', 'identifier')
        if token == 'colon':
            # ID: PATTERN (Exit Section | Enter (SECTION_ID | Section))?
            self.parse_rule(name_or_action, None)
        elif token == 'identifier':
            if name_or_action.lower() == 'reserve':
                # Reserve ID\
                self.rules_file[-1].reserved_ids.append(self.ReservedID(text))
            elif name_or_action.lower() == 'let':
                # Let ID = PATTERN
                self.lexer.skip('whitespace')
                self.lexer.expect('equals')
                self.parse_definition(text)
            elif name_or_action.lower() == 'section':
                # Section SECTION_ID
                new_section = self.Section(text)
                self.rules_file[-1].standalone_sections.append(new_section)
                self.rules_file.append(new_section)
            elif name_or_action.lower() == 'end' and text.lower() == 'section':
                # End Section
                if len(self.rules_file) < 2:
                    self.lexer.throw('"End Section" statement when not in a section')
                old_section = self.rules_file.pop()
            else:
                # ACTION ID: PATTERN (Exit Section | Enter (SECTION_ID | Section))?
                self.lexer.skip('whitespace')
                self.lexer.expect('colon')
                self.parse_rule(text, name_or_action)
        self.lexer.skip('whitespace', 'comment')
        self.lexer.expect('newline')
                
    def parse_rule(self, name, action):
        """
        Parse an expression and add the rule to the current section
        @return: None
        """
        self.lexer.skip('whitespace')
        expression = self.parse_expression()
        self.lexer.skip('whitespace')
        rule = self.Rule(name, expression, action)
        self.rules_file[-1].rules.append(rule)
        if self.lexer.token == 'identifier':
            keyword = self.lexer.expect_keywords('enter', 'exit').lower()
            self.lexer.skip('whitespace')
            if keyword == 'enter':
                rule.section_action = 'enter'
                self.lexer.skip('whitespace')
                text = self.lexer.expect('identifier')
                if text.lower() == 'section':
                    rule.section = self.Section(name)
                    self.rules_file.append(rule.section)
                else:
                    rule.section = self.SectionReference(name)
            elif keyword == 'exit':
                rule.section_action = 'exit'
                self.expect_keywords('section')

    def parse_definition(self, name):
        """
        Parse an expression and add the define to the current section
        @param name: the ID of the definition being parsed
        @return: None
        """
        self.lexer.skip('whitespace')
        expression = self.parse_expression()
        define = self.Define(name, expression)
        self.rules_file[-1].defines.append(define)
        
    def parse_expression(self):
        """
        Parse a concatenated list of regular expression strings and return
        @return: a Pattern object representing the expression
        """
        self.lexer.skip('whitespace')
        is_case_insensitive = False
        if self.lexer.token == 'identifier' and self.lexer.text == 'i':
            is_case_insensitive = True
            self.lexer.get_next()
        string_value = self.lexer.expect_string()
        self.lexer.skip('whitespace')
        while self.lexer.token == 'plus':
            self.lexer.get_next()
            self.lexer.skip('whitespace', 'newline', 'comment')
            string_value += self.lexer.expect_string()
            self.lexer.skip('whitespace')
        return self.Pattern(string_value, is_case_insensitive)
        