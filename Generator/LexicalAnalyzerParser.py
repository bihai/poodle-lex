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

import re

class LexicalAnalyzerParserException(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message
        
    def __repr__(self):
        return self.message

class LexicalAnalyzerLexer(object):
    """
    Reads a rules definition file and provides an iterable stream of tokens
    """
    _patterns = [
        ("comment", r"#[^\r\n]*"),
        ("whitespace", r"[ \t]+"),
        ("newline", r"\r\n|\r|\n"),
        ("colon", r"\:"),
        ("equals", r"="),
        ("identifier", r"[A-Za-z][A-Za-z0-9_]*"),
        ("literalsingle", r"'(?:''|[^'])*'"),
        ("literaldouble", r'"(?:""|[^"])*"'),
        ("plus", r'\+')
    ]
    _pattern = "|".join(["(?P<%s>%s)" % (key, value) for key, value in _patterns])
    _regex = re.compile(_pattern, re.UNICODE or re.MULTILINE)
    
    def __init__(self, file, encoding):
        """
        @param file: the name of the rules definition file to tokenize
        """
        with open(file, 'r') as f:
            self.source = f.read().decode(encoding)
        self.generator = self._tokens()
        self.token = None
        self.text = None
        
    def __iter__(self):
        return self
        
    def next(self):
        return next(self.generator)
            
    def __next__(self):
        return self.next()
            
    def get_next(self):
        """
        Wrapper around the built-in next() function which returns 'end of stream' if there are no more tokens.
        @return: tuple pair for the next token containing a string with the class of token, and the token text
        """
        self.token, self.text = next(self.generator, ('end of stream', 'end of stream'))
        return self.token, self.text
            
    def skip(self, tokens):
        """
        Returns the first token after skipping a class of tokens
        @param tokens: array of strings containing token classes to skip over
        @return: tuple pair for the next non-skipped token containing a string with the class of token, and a string with the token text
        """
        if self.token is None:
            self.get_next()
        while self.token in tokens:
            self.get_next()
        return self.token, self.text
                
    def expect_one_of(self, expected_tokens):
        """
        Checks if the next token is one of a set of token classes. Raises exception if token doesn't match.
        If existin_token and existing_text are provided they will be checked. Otherwise, a token will be pulled from the iterator.
        @param expected_tokens: array of strings containing valid token classes for the next token
        @return: tuple pair for the token being checked containing a string with the class of token, and a string with the token text.
        """
        if self.token is None:
            self.get_next()
        if self.token not in expected_tokens:
            raise LexicalAnalyzerParserException("Expected %s, found '%s'" % (" or ".join(['%s' % i for i in expected_tokens]), self.text))
        old_token, old_text = self.token, self.text
        self.get_next()
        return old_token, old_text
        
    def expect(self, expected_token):
        """
        Check if the next token matches a specific class. Wrapper arond expect_one_of or a single valid class
        @param expected_token: string containing valid token class for the next token
        @return string containing text for the token being checked.
        """
        return self.expect_one_of([expected_token])[1]
        
        
    def _tokens(self):
        """
        Iterator generator which pulls token ids, and token values from text.
        @return: tuple pair for the next token containing a string with the class of token, and a string with the token text.
        """
        index = 0
        while index < len(self.source):
            match = LexicalAnalyzerLexer._regex.match(self.source, index)
            if match is None:
                raise LexicalAnalyzerParserException("Unrecognized character: '%s'" % self.source[index])
            yield [(k, v) for k, v in match.groupdict().iteritems() if v is not None][0]
            index = match.end()
            
# Parse returns an iterator for each rule in the file
def parse(file, encoding):
    """
    Parses a rules definition file and returns an iterator for each rule.
    @param file: the filename of the rules definition file to parse
    @return: iterator which yeields a tuple triplet for each rule in the file containing the following:
        1. a string containing the rule name
        2. a string containing the rule pattern
        3. a boolean which is true of the rule is case insensitive
    """
    def parse_literal(file_lexer):
        token, text = file_lexer.expect_one_of(['literalsingle', 'literaldouble'])
        if token == 'literalsingle':
            return text[1:-1].replace("''", "'")
        else:
            return text[1:-1].replace('""', '"')

    def parse_rule(file_lexer):
        rule_name = file_lexer.text
        rule_is_case_insensitive = False
        rule_pattern = ""
        rule_action = None
        try:
            file_lexer.get_next()
            file_lexer.skip(['whitespace'])
            token, text = file_lexer.expect_one_of(['colon', 'identifier'])
            if token == 'identifier':
                rule_action = rule_name
                rule_name = text
                file_lexer.skip(['whitespace'])
                if rule_action.lower() == 'let':
                    rule_action = '::define::'
                    file_lexer.expect('equals')
                else:
                    file_lexer.expect('colon')                
            
            file_lexer.skip(['whitespace'])
            if file_lexer.token == 'identifier' and file_lexer.text == 'i':
                rule_is_case_insensitive = True
                file_lexer.get_next()
            rule_pattern = parse_literal(file_lexer)
            file_lexer.skip(['whitespace'])
            while file_lexer.token == 'plus':
                file_lexer.get_next()
                file_lexer.skip(['whitespace', 'comment', 'newline'])
                rule_pattern += parse_literal(file_lexer)
                file_lexer.skip(['whitespace'])
            file_lexer.skip(['comment'])
            file_lexer.expect_one_of(['newline', 'end of stream'])
            return rule_name, rule_pattern, rule_is_case_insensitive, rule_action
        except LexicalAnalyzerParserException as e:
            raise LexicalAnalyzerParserException("In rule '%s', %s" % (rule_name, e.message))

    file_lexer = LexicalAnalyzerLexer(file, encoding)
    file_lexer.skip(['whitespace', 'newline'])
    while file_lexer.token != 'end of stream':
        if file_lexer.token == 'comment':
            file_lexer.get_next()
            file_lexer.expect_one_of(['newline', 'end of stream'])
        elif file_lexer.token == 'identifier':
            yield parse_rule(file_lexer)
        else:
            raise LexicalAnalyzerParserException("Expected rule, found '%s'" % file_lexer.text)

        file_lexer.skip(['whitespace', 'newline'])
