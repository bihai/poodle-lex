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

import Regex
from RegexExceptions import *

class RegexParser(object):
    """
    Converts a string containing a regular expression into a visitable regular expression object.
    """
    lowercase = u'abcdefghijklmnopqrstuvwxyz'
    upper = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    number = u'0123456789'
    special = u'(){[.^$*+?|'
    
    def __init__(self, text, is_case_insensitive=False):
        """
        @param text: string containing the regular expression
        @param is_case_insensitive: boolean which is true if the regular expression should be case insensitive
        """
        self.text = text
        self.index = 0
        self.is_case_insensitive = is_case_insensitive
        
    def parse(self):
        """
        Parse the string from its current index and return a regular expression
        @return: a visitable regular expression object from the Regex package
        """
        return self.parse_alternation()
        
    def parse_alternation(self):
        """
        Parse the string from its current index into an alternation or an expression that can be contained by an alternation.
        @return: a visitable regular expression object from the Regex package.
        """
        concatenations = [self.parse_concatenation()]
        while self.index < len(self.text) and self.text[self.index] == u'|':
            self.index += 1
            concatenations.append(self.parse_concatenation())
        if len(concatenations) > 1:
            return Regex.Alternation(concatenations)
        else: 
            return concatenations[0]
    
    def parse_concatenation(self):
        """
        Parse the string from its current index into a concatenation or an expression that can be contained by an concatenation.
        @return: a visitable regular expression object from the Regex package.
        """
        repetitions = []
        while self.text[self.index] not in (u'|', u')'):
            repetitions.append(self.parse_qualified())
            if self.index == len(self.text):
                break
        if len(repetitions) > 1:
            return Regex.Concatenation(repetitions)
        else:
            return repetitions[0]
        
    def parse_qualified(self):
        """
        Parse the string from its current index into a repetition or an expression that can be contained by an repetition.
        @return: a visitable regular expression object from the Regex package.
        """
        child = self.parse_character()
        if self.index == len(self.text):
            return child
        if self.text[self.index] == u'*':
            self.index += 1
            return Regex.Repetition(child, 0, Regex.Repetition.Infinity)
        elif self.text[self.index] == u'+':
            self.index += 1
            return Regex.Repetition(child, 1, Regex.Repetition.Infinity)
        elif self.text[self.index] == u'?':
            self.index += 1
            return Regex.Repetition(child, 0, 1)
        elif self.text[self.index] == u'{':
            self.index += 1
            return self.parse_range(child)
        else:
            return child
            
    def parse_character(self):
        """
        Parse the string from its current index ino a character set or a sub-expression
        @return: a visitable regular expression object from the Regex package.
        """
        if self.text[self.index] == u'[':
            self.index += 1
            return self.parse_character_class()
        
        elif self.text[self.index] == u'(':
            self.index += 1
            child = self.parse()
            self.expect(u')')
            return child
            
        else:
            return self.parse_literal()
            
    def parse_literal(self, suppress_case_insensitive=False):
        """
        Parse a single character from the string, from its current index into a literal expression
        @return: a Regex.Literal or Regex.LiteralExcept object representing the character.
        """
        
        def get_literal(character, is_case_insensitive):
            if is_case_insensitive and not suppress_case_insensitive:
                lowercase = character.lower()
                uppercase = character.upper()
                if lowercase != uppercase:
                    return Regex.Literal(lowercase + uppercase)
            return Regex.Literal(character)
                
        if self.text[self.index] == u'\\':
            self.index += 2
            if self.text[self.index-1] == u'w':
                return Regex.Literal(RegexParser.upper + RegexParser.lower + RegexParser.number + u'_')
            elif self.text[self.index-1] == u'W':
                return Regex.LiteralExcept(RegexParser.upper + RegexParser.lower + RegexParser.number + u'_')
            elif self.text[self.index-1] == u'r':
                return Regex.Literal(u'\r')
            elif self.text[self.index-1] == u'n':
                return Regex.Literal(u'\n')
            elif self.text[self.index-1] == u't':
                return Regex.Literal(u'\t')
            elif self.text[self.index-1] == u's':
                return Regex.Literal(u' ')
            elif self.text[self.index-1] == u'd':
                return Regex.Literal(RegexParser.number)
            else:
                return get_literal(self.text[self.index-1], self.is_case_insensitive)

        else:
            self.index += 1
            if self.text[self.index-1] in RegexParser.special:
                raise RegexParserInvalidCharacter(character)
            return get_literal(self.text[self.index-1], self.is_case_insensitive)
            
    def parse_repetition(self, child):
        """
        Parse a {min, max} expression from the string at its current index
        @param child: a visital object from the Regex package containing the repeated expression.
        @return: a Regex.Repetition object representing the repetition.
        """
        first = self.parse_integer()
        self.expect(u',')
        last = self.parse_integer()
        self.expect(u'}')
        return Regex.Repetition(child, first, last)
    
    def parse_integer(self):
        """
        Parse an integer from the string at its current index.
        @return: the integer parsed from the string.
        """
        if self.text[self.index] not in RegexParser.number:
            raise RegexParserExpected(u'number', self.text, self.index)
        while self.text[self.index] in RegexParser.number:
            number += self.text[self.index]
            self.index += 1
        return int(number)
    
    def expect(self, character):
        """
        Raise an exception if the character at the current index of the string is not a specific value.
        @param character: the value that the current character should be.
        """
        if self.index >= len(self.text) or self.text[self.index] != character:
            raise RegexParserExpected(unicode(character), self.text, self.index)
        self.index += 1
        
    def parse_character_class(self):
        """
        Parse a character class ([...]) expression from the string at its current index.
        @return: a Regex.Literal or Regex.LiteralExcept object representing the characters
        """
        if self.index < len(self.text):
            inverse = False
            if self.text[self.index] == u'^':
                inverse = True
                self.index += 1
            characters = list(self.parse_character_range().characters)
            while self.text[self.index] != u']':
                characters.extend(self.parse_character_range().characters)
        self.expect(u']')
        
        if inverse:
            return Regex.LiteralExcept(characters)
        else:
            return Regex.Literal(characters)
    
    def parse_character_range(self):
        """
        Parse a range (e.g. a-z) expression from the string at its current index
        @return: a string containing all the characters in the range
        """
        start_literal = self.parse_literal(True)
        if self.text[self.index] == u'-':
            self.index += 1
            end_literal = self.parse_literal(True)
        else:
            return start_literal
        
        # Range must be two single characters with the end having a larger value than the start
        start_ordinal = ord(start_literal.characters[0])
        end_ordinal = ord(end_literal.characters[0])
        if len(start_literal.characters) > 1 or len(end_literal.characters) > 1:
            raise RegexParserInvalidCharacterRange(start_literal.characters, end_literal.characters)
        elif start_ordinal > end_ordinal:
            raise RegexParserInvalidCharacterRange(start_literal.characters[0], end_literal.characters[0])
            
        start_literal.characters = u''.join([unichr(i) for i in range(start_ordinal, end_ordinal+1)])
        if self.is_case_insensitive:
            characters = set(start_literal.characters.upper())
            characters.update(set(start_literal.characters.lower()))
            start_literal.characters = "".join(characters)
            
        return start_literal
        
