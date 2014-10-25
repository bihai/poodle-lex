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

import AST
from Lexer import RulesFileException, Lexer

def parse(file, encoding="utf-8"):
    return Parser(file=file, encoding=encoding).parse()

def parse_stream(stream, encoding="utf-8"):
    return Parser(stream=stream, encoding=encoding).parse()
    
class Parser(object):
    def __init__(self, file=None, stream=None, encoding="utf-8"):
        self.lexer = Lexer(file, stream, encoding)
        for NodeType in [
            AST.Rule,
            AST.Define,
            AST.Pattern,
            AST.Section,
            AST.SectionReference
        ]:
            setattr(self, NodeType.__name__, self.create_line_wrapper(NodeType))
        self.rules_file = [self.Section('::main::', None)]
        
    def create_line_wrapper(self, NodeType):
        """
        Uses reflection to create a version of each task with the line 
        number of the rules file lexer bound to the constructor
        @param NodeType: a Python class to wrap
        """
        parent_self = self
        class Wrapper(NodeType):
            def __init__(self, *args, **kw_args):
                NodeType.__init__(self, *args, line_number=parent_self.lexer.line, **kw_args)
        Wrapper.__name__ = NodeType.__name__ + 'Wrapper'
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
            
        if len(self.rules_file) > 1:
            raise RulesFileException("'Section' without 'End Section'")
        return self.rules_file.pop()
        
    def parse_statement(self):
        """
        Parse parse a single statement in the rules file, and attach it
        to the AST object
        @return: None
        """
        list_is_keyword = lambda x, y: len(x) == 1 and x[0].lower() == y.lower()    
        
        id, commands = self.parse_commands_and_id()
        self.lexer.skip('whitespace')
        if list_is_keyword(commands, 'let'):
            # Let ID = PATTERN
            self.lexer.expect('equals')
            self.lexer.skip('whitespace')
            self.parse_definition(id)
        elif len(commands) == 0 and id is not None and id.lower() == 'skip':
            # Skip: RULE
            self.lexer.expect('colon')
            self.parse_rule(None, 'skip')
        elif list_is_keyword(commands, 'section'):
            # Section ID
            self.lexer.skip('whitespace')
            attributes = self.parse_section_attributes()
            inherits = 'inherits' in attributes
            exits = 'exits' in attributes
            new_section = self.Section(id, self.rules_file[-1], inherits=inherits, exits=exits)
            self.rules_file[-1].add_scope('section', new_section)
            self.rules_file.append(new_section)
        elif list_is_keyword(commands, 'end') and id.lower() == 'section':
            # End Section
            if len(self.rules_file) < 2:
                self.lexer.throw('"End Section" statement when not in a section')
            self.rules_file.pop()
        else:
            # (COMMAND (,COMMAND)*)? ID: RULE
            if self.lexer.token in ('colon', 'literalsingle', 'literaldouble'):
                self.lexer.expect('colon')
            self.parse_rule(id, commands)
        self.lexer.skip('whitespace', 'comment')
        self.lexer.expect_one_of('newline', 'endofstream')
        
    def parse_commands_and_id(self):
        """
        Parse out a list of commands followed by an identifier
        @return: tuple with a string of the rule name and a list of commands. If ID is not provided, it is None.
        """
        id = self.lexer.expect('identifier')
        commands = []
        self.lexer.skip('whitespace')
        while self.lexer.token == 'comma':
            self.lexer.expect('comma')
            self.lexer.skip('whitespace')
            commands.append(self.lexer.expect('identifier'))
            self.lexer.skip('whitespace')
        if len(commands) > 0:
            commands.insert(0, id)
            id = None
        if id is None:
            id = self.lexer.expect('identifier')
        elif self.lexer.token == 'identifier':
            commands.append(id)
            id = self.lexer.expect('identifier')
            
        if len(commands) == 0 and id.lower() == 'skip':
            # Special case: command "skip" can be used without identifier
            return None, [id]
        else:
            return id, commands

    def parse_rule(self, name, actions):
        """
        Parse an expression and add the rule to the current section
        @return: None
        """
        self.lexer.skip('whitespace', 'comment')
        if self.lexer.token in ['newline', 'endofstream'] or self.lexer.is_keyword('enter', 'exit', 'switch'):
            expression = None
        else:
            expression = self.parse_expression()
        self.lexer.skip('whitespace')
        rule = self.Rule(name, expression, actions)
        self.rules_file[-1].add('rule', rule)
        if self.lexer.token == 'identifier':
            keyword = self.lexer.expect_keywords('enter', 'exit', 'switch').lower()
            self.lexer.skip('whitespace')
            if keyword == 'enter' or keyword == 'switch':
                self.lexer.skip('whitespace')
                text = self.lexer.expect('identifier')
                if text.lower() == 'section':
                    section = self.Section(name, self.rules_file[-1])
                    self.lexer.skip('whitespace')
                    attributes = self.parse_section_attributes()
                    section.inherits = 'inherits' in attributes
                    section.exits = 'exits' in attributes
                    rule.section_action = (keyword, section)
                    self.rules_file[-1].add_scope('section', section)
                    self.rules_file.append(section)
                else:
                    rule.section_action = (keyword, self.SectionReference(text))
            elif keyword == 'exit':
                rule.section_action = ('exit', None)
                self.lexer.expect_keywords('section')
                
    def parse_definition(self, name):
        """
        Parse an expression and add the define to the current section
        @param name: the ID of the definition being parsed
        @return: None
        """
        self.lexer.skip('whitespace')
        expression = self.parse_expression()
        define = self.Define(name, expression)
        self.rules_file[-1].add('define', define)
        
    def parse_expression(self):
        """
        Parse a concatenated list of regular expression strings and return
        @return: a Pattern object representing the expression
        """
        self.lexer.skip('whitespace')
        attributes = AST.PatternAttributes(False, False, False)
        history = {}
        if self.lexer.token == 'identifier':
            for letter in self.lexer.text.lower():
                if letter in history:
                    raise RulesFileException("Duplicate attribute '{id}'".format(id=letter))
                if letter == 'i':
                    attributes.is_case_insensitive = True
                elif letter == 'l':
                    attributes.is_literal = True
                elif letter == 'u':
                    attributes.is_unicode_default = True
                else:
                    raise RulesFileException("Unrecognized attribute '{id}'".format(id=letter))
                history[letter] = True
            self.lexer.get_next()
        string_value = self.lexer.expect_string()
        self.lexer.skip('whitespace')
        while self.lexer.token == 'plus':
            self.lexer.get_next()
            self.lexer.skip('whitespace', 'newline', 'comment')
            string_value += self.lexer.expect_string()
            self.lexer.skip('whitespace')
        return self.Pattern(string_value, attributes)
        
    def parse_section_attributes(self):
        """
        Parse a comma-delimited list of section attributes
        """
        attributes = set()
        while self.lexer.is_keyword('inherits', 'exits'):
            keyword = self.lexer.expect('identifier').lower()
            if keyword in attributes:
                raise Exception("duplicate attribute '{keyword}'".format(keyword=keyword))
            attributes.add(keyword)
            self.lexer.skip('whitespace')
            if self.lexer.token == 'comma':
                self.lexer.get_next()
                self.lexer.skip('whitespace')
            else:
                break
        return attributes
        