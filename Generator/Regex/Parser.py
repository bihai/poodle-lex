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

import string
import Regex
from ..CoverageSet import CoverageSet
from Exceptions import *

class Parser(object):
    """
    Converts a string containing a regular expression into a visitable regular expression object.
    """
    lowercase = (ord('a'), ord('z'))
    uppercase = (ord('A'), ord('Z'))
    digits = (ord('0'), ord('9'))
    underscore = (ord('_'), ord('_'))
    tab = (9, 9)
    line_feed = (10, 10)
    vertical_tab = (11, 11)
    form_feed = (12, 12)
    carriage_return = (13, 13)
    space = ((ord(' '), ord(' ')))
    special = u'(){[.^$*+?|:'
    
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
        regex_object = self.parse_alternation()
        if self.index < len(self.text):
            self.expect(u'end of pattern')
        return regex_object
        
    def parse_alternation(self):
        """
        Parse the string from its current index into an alternation or an expression that can be contained by an alternation.
        @return: a visitable regular expression object from the Regex package.
        """
        concatenations = [self.parse_concatenation()]
        while self.get_next_if(u'|'):
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
        repetitions = [self.parse_qualified()]
        while self.next_is_not(u'|)'):
            repetitions.append(self.parse_qualified())
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
        if self.get_next_if(u'*'):
            return Regex.Repetition(child, 0, Regex.Repetition.Infinity)
        elif self.get_next_if(u'+'):
            return Regex.Repetition(child, 1, Regex.Repetition.Infinity)
        elif self.get_next_if(u'?'):
            return Regex.Repetition(child, 0, 1)
        # Need to look ahead two characters because it might be a variable following this one
        elif self.next_is(u'{') and self.nth_next_is_not(2, string.ascii_letters + '.'):
            self.get_next()
            return self.parse_repetition(child)
        else:
            return child
            
    def parse_character(self):
        """
        Parse the string from its current index ino a character set or a sub-expression
        @return: a visitable regular expression object from the Regex package.
        """
        if self.get_next_if(u'['):
            return self.parse_character_class()
        
        elif self.get_next_if(u'('):
            child = self.parse_alternation()
            self.expect(u')')
            return child
        
        elif self.get_next_if(u'{'):
            return self.parse_variable()
            
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
                    return Regex.Literal([(ord(lowercase), ord(lowercase)), (ord(uppercase), ord(uppercase))])
            return Regex.Literal([(ord(character), ord(character))])

        if self.get_next_if(u'.'):
            return Regex.Literal([(1, 0x10FFFF)])
        elif self.get_next_if(u'\\'):
            if self.get_next_if(u'w'):
                return Regex.Literal([Parser.lowercase, Parser.uppercase, Parser.underscore])
            elif self.get_next_if(u'W'):
                return Regex.LiteralExcept([Parser.lowercase, Parser.uppercase, Parser.underscore])
            elif self.get_next_if(u'r'):
                return Regex.Literal([Parser.carriage_return])
            elif self.get_next_if(u'n'):
                return Regex.Literal([Parser.line_feed])
            elif self.get_next_if(u't'):
                return Regex.Literal([Parser.tab])
            elif self.get_next_if(u's'):
                return Regex.Literal([Parser.space])
            elif self.get_next_if(u'd'):
                return Regex.Literal([Parser.digits])
            elif self.get_next_if(u'v'):
                return Regex.Literal([Parser.vertical_tab])
            elif self.get_next_if(u'f'):
                return Regex.Literal([Parser.form_feed])
            elif self.get_next_if(u'x'):
                codepoint = self.parse_hex_digits(2)
                return Regex.Literal([(codepoint, codepoint)])
            elif self.get_next_if(u'u'):
                codepoint = self.parse_hex_digits(4)
                return Regex.Literal([(codepoint, codepoint)])
            elif self.get_next_if(u'U'):
                codepoint = self.parse_hex_digits(6)
                return Regex.Literal([(codepoint, codepoint)])
            else:
                return get_literal(self.get_next(), self.is_case_insensitive)
        else:
            character = self.get_next()
            if character in Parser.special:
                raise RegexParserInvalidCharacter(character)
            return get_literal(character, self.is_case_insensitive)
   
    def parse_hex_digits(self, num_digits):
        hex_text = ''
        for i in range(num_digits):
            if not self.next_is(string.hexdigits):
                self.expect(string.hexdigits, name='hexadecimal digit')
            hex_text += self.get_next()
        value = int(hex_text, 16)
        if (value > 0x10ffff):
            raise RegexParserUnicodeCodepointOutOfRange(value)
        return value
        
    def parse_variable(self):
        """
        Parse a variable instance from the string at its current index
        @return: a Regex.Variable object representing the variable instance
        """
        variable_name = ''
        while self.next_is(string.ascii_letters + '.'):
            variable_name += self.get_next()
        self.expect("}")
        return Regex.Variable(variable_name)
    
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
        if first > last:
            raise RegexParserExceptionInternal("Minimum repetition (%d) cannot be larger than maximum repetition (%d)." % (first, last))
        return Regex.Repetition(child, first, last)
    
    def parse_integer(self):
        """
        Parse an integer from the string at its current index.
        @return: the integer parsed from the string.
        """
        number = ''
        if not self.next_is(string.digits):
            self.expect(u'integer')
        while self.next_is(string.digits):
            number += self.get_next()
        return int(number)
    
    def expect(self, character, name=None):
        """
        Raise an exception if the character at the current index of the string is not a specific value.
        @param character: the value that the current character should be.
        """
        if not self.next_is(character):
            if name is None:
                raise RegexParserExpected(unicode(character), self.text, self.index)
            else:
                raise RegexParserExpected(name, self.text, self.index)
        self.index += 1
        
    def get_next(self):
        """
        Returns the next character, advances the stream, and throws an exception if at the end of the pattern
        @return: String containing the next character
        """
        if self.index >= len(self.text):
            self.expect('character')
        self.index += 1
        return unicode(self.text[self.index-1])
        
    def get_next_if(self, characters):
        """
        Advances the sream if the next character is one of a set of characters
        @param characters: A string containing the characters for which to check
        @return: Boolean if the next character is one of characters
        """
        if self.next_is(characters):
            self.get_next()
            return True
        return False
        
    def next_is(self, characters):
        """
        Returns true if the next character is at the current index of the string is one of a set of characters. False if not.
        @param characters: the value that the current character should be.
        @return: True if the next characters is in the expected set, False otherwise or if at end of string
        """
        return self.nth_next_is(1, characters)
        
    def nth_next_is(self, n, characters):
        """
        Looks ahead n characters and returns true if the next nth character of the string is one of a set of characters. False if not.
        @param n: how many characters to look ahead. Must be greater than 0
        @param characters: the value that the current character should be.
        @return: True if the next characters is in the expected set, False otherwise or if at end of string
        """
        return n > 0 and self.index + n-1 < len(self.text) and self.text[self.index+n-1] in characters

    def next_is_not(self, characters):
        """
        Returns true if the next character is not end-of-string and is not one of a set of characters. False if not
        @param characters: the value that the current character should not be.
        @return: True if the next character is not in the expected set, Fase otherwise or if at end of string
        """
        return self.index < len(self.text) and self.text[self.index] not in characters
        
    def nth_next_is_not(self, n, characters):
        """
        Looks ahead n characters and returns true if the next nth character of the string is not one of a set of characters. False if not.
        @param n: how many characters to look ahead. Must be greater than 0
        @param characters: the value that the current character should be.
        @return: True if the next characters is in the expected set, False otherwise or if at end of string
        """
        return n > 0 and self.index + n-1 < len(self.text) and self.text[self.index+n-1] not in characters
        
    def parse_character_class(self):
        """
        Parse a character class ([...]) expression from the string at its current index.
        @return: a Regex.Literal or Regex.LiteralExcept object representing the characters
        """
        inverse = False
        if self.get_next_if(u'^'):
            inverse = True
        characters = self.parse_character_range().characters
        while self.next_is_not(u']'):
            characters.update(self.parse_character_range().characters)
        self.expect(u']')
        
        if inverse:
            return Regex.LiteralExcept([i for i in characters])
        else:
            return Regex.Literal([i for i in characters])
    
    def parse_named_character_class(self):
        classes = {
            u"alnum": [Parser.lowercase, Parser.uppercase, Parser.digits],
            u"word": [Parser.lowercase, Parser.uppercase, Parser.digits, Parser.underscore],
            u"alpha": [Parser.uppercase, Parser.lowercase],
            u"blank": [Parser.space, Parser.tab],
            u"cntrl": [(0, 31)],
            u"digit": [Parser.digits],
            u"graph": [(33, 127)],
            u"lower": [Parser.lowercase],
            u"print": [(32, 127)],
            u"punct": [(ord(i), ord(i)) for i in "][!\"#$%&'()*+,./:;<=>?@\\^_`{|}~-"],
            u"space": [(ord(i), ord(i)) for i in string.whitespace],
            u"xdigit": [Parser.digits, (ord('a'), ord('f')), (ord('A'), ord('F'))]
        }
        self.expect(u':')
        class_name = ""
        while self.next_is(string.ascii_letters):
            class_name += self.get_next()
        self.expect(":")
        self.expect("]")
        
        if class_name in classes:
            return Regex.Literal(classes[class_name])
        else:
            raise RegexParserExceptionInternal("Character class '%s' not recognized" % class_name)

    def parse_character_range(self):
        """
        Parse a range (e.g. a-z) expression from the string at its current index
        @return: a string containing all the characters in the range
        """
        if self.get_next_if(u'['):
            return self.parse_named_character_class()
        start_literal = self.parse_literal(True)
        if self.get_next_if(u'-'):
            end_literal = self.parse_literal(True)
        else:
            return start_literal
        
        # Range must be two single characters with the end having a larger value than the start
        if len(start_literal.characters) > 1 or len(end_literal.characters) > 1:
            raise RegexParserInvalidCharacterRange(start_literal.characters, end_literal.characters)
        start_ordinal = next(iter(start_literal.characters))[0]
        end_ordinal = next(iter(end_literal.characters))[0]
        if start_ordinal > end_ordinal:
            raise RegexParserInvalidCharacterRange(unichr(start_ordinal), unichr(end_ordinal))
        
        if self.is_case_insensitive:
            lower_start = ord(unichr(start_ordinal).lower())
            lower_end = ord(unichr(end_ordinal).lower())
            upper_start = ord(unichr(start_ordinal).upper())
            upper_end = ord(unichr(end_ordinal).upper())
            return Regex.Literal([(lower_start, lower_end), (upper_start, upper_end)])
        else:
            return Regex.Literal([(start_ordinal, end_ordinal)])
        