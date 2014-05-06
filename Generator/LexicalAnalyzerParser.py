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

import LexicalAnalyzer
from RegexParser import RegexParser
from LexicalAnalyzerLexer import LexicalAnalyzerParserException, LexicalAnalyzerLexer

class LexicalAnalyzerParser(object):
    def __init__(self, file, encoding):
        self.lexer = LexicalAnalyzerLexer(file, encoding)
        self.rules_file = LexicalAnalyzer.LexicalAnalyzer()
        
    def parse(self):
        """
        Parse the rules file and return a string
        @return: a LexicalAnalyzer object described by the rules file
        """
        self.lexer.skip('whitespace', 'comment', 'newline')
        while self.lexer.token != 'end of stream':
            self.parse_statement()
            self.lexer.skip('whitespace', 'comment', 'newline')
        return self.rules_file
        
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
            self.parse_rule(name_or_action, None)
        elif token == 'identifier':
            if name_or_action.lower() == 'reserve':
                self.rules_file.reserve_id(text)
            elif name_or_action.lower() == 'let':
                self.lexer.skip('whitespace')
                self.lexer.expect('equals')
                self.parse_definition(text)
            else:
                self.lexer.skip('whitespace')
                self.lexer.expect('colon')
                self.parse_rule(text, name_or_action)
        self.lexer.skip('whitespace', 'comment')
        self.lexer.expect('newline')
                
    def parse_rule(self, name, action):
        """
        Parse an expression and add the rule to the LexicalAnalyzer object
        @return: None
        """
        self.lexer.skip('whitespace')
        expression = self.parse_expression()
        self.rules_file.add_rule(name, expression, action)
        
    def parse_definition(self, name):
        """
        @return: None
        """
        self.lexer.skip('whitespace')
        expression = self.parse_expression()
        self.rules_file.add_define(name, expression)
        
    def parse_expression(self):
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
        return LexicalAnalyzer.Pattern(string_value, is_case_insensitive)
        