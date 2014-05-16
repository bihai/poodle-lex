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

class RulesFileException(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message
        
    def __repr__(self):
        return self.message

class Lexer(object):
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
        ("literalsingle", r"'(?:''|[^'\r\n])*'"),
        ("literaldouble", r'"(?:""|[^"\r\n])*"'),
        ("plus", r'\+'),
        ("leftparenthesis", r'\('),
        ("rightparenthesis", r'\)')
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
        self.line = 1
        
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
        if self.token == 'newline':
            self.line += 1
        self.token, self.text = next(self.generator, ('end of stream', 'end of stream'))
        return self.token, self.text
        
    def throw(self, message):
        raise RulesFileException('On line %d, %s' % (self.line, message))
            
    def skip(self, *tokens):
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
        
    def expect_string(self):
        """
        Parses a double or single-quoted string, strips quotes, and removes escaped quotes
        @return: the value of the string constant parsed
        """
        if self.token is None:
            self.get_next()
        token, text = self.expect_one_of('literalsingle', 'literaldouble')
        if token == 'literalsingle':
            return text[1:-1].replace("''", "'")
        else:
            return text[1:-1].replace('""', '"')
                
    def expect_one_of(self, *expected_tokens):
        """
        Checks if the next token is one of a set of token classes. Raises exception if token doesn't match.
        If existin_token and existing_text are provided they will be checked. Otherwise, a token will be pulled from the iterator.
        @param expected_tokens: one or more strings containing valid token classes for the next token
        @return: tuple pair for the token being checked containing a string with the class of token, and a string with the token text.
        """
        if self.token is None:
            self.get_next()
        if self.token not in expected_tokens:
            self.throw("Expected %s, found '%s'" % (" or ".join(['%s' % i for i in expected_tokens]), self.text))
        old_token, old_text = self.token, self.text
        self.get_next()
        return old_token, old_text
        
    def expect_keywords(self, *expected_text):
        """
        Checks that the next token is an identifier and that without casing it is one of an expected set of values
        @param expected_text: one or more strings containing valid values for the next token
        """
        if self.token is None:
            self.get_next()
        if self.token != 'identifier' or self.text.lower() not in [i.lower() for i in expected_text]:
            self.throw("Expected '%s', found '%s'" % ("' or '".join(expected_text), self.text))
        old_token, old_text = self.token, self.text
        self.get_next()
        return old_text
        
    def expect(self, expected_token):
        """
        Check if the next token matches a specific class. Wrapper arond expect_one_of or a single valid class
        @param expected_token: string containing valid token class for the next token
        @return string containing text for the token being checked.
        """
        return self.expect_one_of(expected_token)[1]
        
    def _tokens(self):
        """
        Iterator generator which pulls token ids, and token values from text.
        @return: tuple pair for the next token containing a string with the class of token, and a string with the token text.
        """
        index = 0
        while index < len(self.source):
            match = Lexer._regex.match(self.source, index)
            if match is None:
                self.throw("unrecognized syntax starting with '%s'" % self.source[index])
            yield [(k, v) for k, v in match.groupdict().iteritems() if v is not None][0]
            index = match.end()
            