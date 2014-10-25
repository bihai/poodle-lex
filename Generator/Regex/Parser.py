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
from UnicodeQuery import UnicodeQuery

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
    special = u'(){}[].^$*+-~&?|:'
    closing = u')}]'
    unicode_db = UnicodeQuery.find_db()
    set_operators = "-&~|"
    
    def __init__(self, text, is_case_insensitive=False, is_unicode_defaults=False, is_literal=False, unicode_db=None):
        """
        @param text: string containing the regular expression
        @param is_case_insensitive: boolean which is true if the regular expression should be case insensitive
        @param unicode_db: location of the folder containing the JSON unicode property data files
        """
        self.text = text
        self.index = 0
        self.is_case_insensitive = is_case_insensitive
        self.is_unicode_defaults = is_unicode_defaults
        self.is_literal = is_literal
        if unicode_db is not None:
            self.unicode_db = unicode_db
        elif Parser.unicode_db is None and unicode_db is None:
            raise ValueError("Unicode database not found and no database provided")
        
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
            elif self.get_next_if(u'p'):
                coverage = self.parse_unicode_expression()
                return Regex.Literal(coverage)
            elif self.get_next_if(u'N'):
                coverage = self.parse_unicode_name()
                return Regex.Literal(coverage)
            elif self.get_next_if(u'P'):
                coverage = self.parse_unicode_expression()
                return Regex.LiteralExcept(coverage)
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
            if character in Parser.closing:
                raise RegexParserExpected("character", self.text, self.index-1)
            elif character in Parser.special:
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

    def next_is_set_operator(self):
        return self.next_is(Parser.set_operators) and self.nth_next_is(2, self.text[self.index])
        
    def parse_character_class(self):
        """
        Parse a character class ([...]) expression from the string at its current index.
        @return: a Regex.Literal object representing the characters
        """
        characters = self.parse_character_class_expression()
        return Regex.Literal([i for i in characters])
    
    def parse_named_character_class(self):
        """
        Parse a named character class ([:...:]) subexpresion from the string at its current index.
        @return: a CoverageSet object covering all the characters covered by the named class
        """
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
            u"xdigit": [Parser.digits, (ord('a'), ord('f')), (ord('A'), ord('F'))],
            u"upper": [Parser.uppercase]
        }
        unicode_classes = {
            u"alnum": {False: [('alpha', None), ('digit', None)], True: []},
            u"word": {False: [('alpha', None), ('gc', 'Mark'), ('digit', None), ('gc', 'Connector_Punctuation'), ('Join_Control', None)], True: []},
            u"alpha": {False: [('alpha', None)], True: []},
            u"blank": {False: [('gc', 'Space_Separator'), ('na1', 'CHARACTER TABULATION')], True: []},
            u"cntrl": {False: [('gc', 'Control')], True: []},
            u"digit": {False: [('gc', 'Decimal_Number')], True: []},
            u"graph": {False: [], True: [('space', None), ('gc', 'Control'), ('gc', 'Surrogate'), ('gc', 'Unassigned')]},
            u"lower": {False: [('Lowercase', None)], True: []},
            u"print": {False: [('gc', 'Space_Separator'), ('na1', 'CHARACTER TABULATION')], True: [('space', None), ('gc', 'Control'), ('gc', 'Surrogate'), ('gc', 'Unassigned')]},
            u"punct": {False: [('gc', 'Punctuation')], True: []},
            u"space": {False: [('Whitespace', None)], True: []},
            u"xdigit": {False: [('gc', 'Decimal_Number'), ('Hex_Digit', None)], True: []},
            u"upper": {False: [('Uppercase', None)], True: []}
        }
        
        self.expect(u':')
        class_name = ""
        while self.next_is(string.ascii_letters):
            class_name += self.get_next()
        self.expect(":")
        self.expect("]")
        
        if self.is_unicode_defaults and class_name in unicode_classes:
            class_queries = unicode_classes[class_name]
            instance = UnicodeQuery.instance(self.unicode_db)
            coverage = CoverageSet()
            for k, v in class_queries[False]:
                coverage.update(instance.query(k, v))
            if len(class_queries[True]) > 0:
                inverted_coverage = CoverageSet([(1, 0x10ffff)])
                for k, v in class_queries[True]:
                    inverted_coverage.difference_update(instance.query(k, v))
                coverage.update(inverted_coverage)
            return coverage
                
        elif not self.is_unicode_defaults and class_name in classes:
            return CoverageSet(classes[class_name])
        else:
            raise RegexParserExceptionInternal("Character class '%s' not recognized" % class_name)
            
    def parse_character_class_subexpression(self):
        """
        Parse either a group "[...]", a named character class "[:...:]", or a range "...-..."
        @returns: a CoverageSet object containing the characters in the sub-expression
        """
        if self.next_is(':'):
            return self.parse_named_character_class()
        expression = self.parse_character_class_expression()
        return expression
            
        return self.parse_character_class_range()
        
    def parse_character_class_character(self):
        """
        Parse a lingle literal, but accomodate sub-expressions such as "[:...:]" or "[...]"
        @return: a CoverageSet object containing the characters that were parsed
        """
        if self.get_next_if(u'['):
            return self.parse_character_class_subexpression()
        else:
            return self.parse_literal(True).characters

    def parse_character_class_range(self):
        """
        Parse a range (e.g. a-z) expression from the string at its current index
        @return: a CoverageSet object containing all the characters in the range
        """
        start_literal = self.parse_character_class_character()
        if self.next_is('-') and not self.nth_next_is(2, '-'):
            self.get_next()
            end_literal = self.parse_character_class_character()
        else:
            return start_literal
        
        # Range must be two single characters with the end having a larger value than the start
        if len(start_literal) > 1 or len(end_literal) > 1:
            raise RegexParserInvalidCharacterRange(start_literal, end_literal)
        start_ordinal = next(iter(start_literal))[0]
        end_ordinal = next(iter(end_literal))[0]
        if start_ordinal > end_ordinal:
            raise RegexParserInvalidCharacterRange(unichr(start_ordinal), unichr(end_ordinal))
        
        if self.is_case_insensitive:
            lower_start = ord(unichr(start_ordinal).lower())
            lower_end = ord(unichr(end_ordinal).lower())
            upper_start = ord(unichr(start_ordinal).upper())
            upper_end = ord(unichr(end_ordinal).upper())
            return CoverageSet([(lower_start, lower_end), (upper_start, upper_end)])
        else:
            return CoverageSet([(start_ordinal, end_ordinal)])
            
    def parse_character_class_terms(self):
        """
        Parse a series of terms within a character class ("a-zbc", etc).
        @returns: the union of their coverage        
        """
        coverage = CoverageSet()
        coverage.update(self.parse_character_class_range())
        while self.next_is_not(']\r\n') and not self.next_is_set_operator():
            coverage.update(self.parse_character_class_range())
        return coverage
        
    def parse_character_class_expression(self):
        """
        Parses the text after the left bracket of a "[...]" expression
        @returns: a CoverageSet object covering all the characters covered by the character class.
        """
        inverse = self.get_next_if(u'^')
        
        coverage = self.parse_character_class_terms()
        while self.next_is_set_operator():
            operator = self.get_next()
            self.get_next()
            if self.next_is(u'])}'):
                raise RegexParserExpected("expression term", self.text, self.index)
            rhs = self.parse_character_class_terms()
            if operator == u'|':
                coverage.update(rhs)
            elif operator == u'&':
                coverage.intersection_update(rhs)
            elif operator == u'-':
                coverage.difference_update(rhs)
            elif operator == u'~':
                intersection = CoverageSet.intersection(coverage, rhs)
                coverage.update(rhs)
                coverage.difference_update(intersection)
        self.expect("]")
        
        if inverse:
            inverted_coverage = CoverageSet()
            inverted_coverage.add(1, 0x10FFFF)
            inverted_coverage.difference_update(coverage)
            return inverted_coverage
        
        return coverage
        
    def parse_unicode_expression(self):
        """
        Parse a unicode "{...}" expression for querying unicode properties.
        @returns: A CoverageSet object containing all characters covered by
            the specified unicode query.
        """
        self.expect("{")
        coverage = self.parse_unicode_subexpression()
        while self.get_next_if(u'|'):
            coverage.update(self.parse_unicode_subexpression())
        self.expect("}")
        return coverage
        
    def parse_unicode_name(self):
        """
        Parse a unicode "{...}" expresion for querying unicode names.
        @returns: A CoverageSet object containing all characters covered by
            the specified unicode query
        """
        self.expect("{")
        name = self.parse_unicode_word()
        coverage = UnicodeQuery.instance(self.unicode_db).query('na', name)
        if coverage.empty():
            raise ValueError("Name '{name}' not found".format(name=name))
        return coverage
        
    def parse_unicode_subexpression(self):
        """
        Parse a single "NAME=VALUE" term for a unicode property.
        @returns: A CoverageSet object containing the values covered by the term
        """
        name = self.parse_unicode_word()
        if self.get_next_if(u':='):
            value = self.parse_unicode_word()
        else:
            value = None
        coverage = UnicodeQuery.instance(self.unicode_db).query(name, value)
        return coverage
        
    def parse_unicode_word(self):
        """
        Scan a string, while skipping over whitespace, hyphens, and underscores.
        @return: the filtered name that was parsed out.
        """
        variable_name = ''
        while True:
            if self.next_is(' \t-_'):
                self.get_next()
            elif self.next_is(string.ascii_letters):
                variable_name += self.get_next()
            else:
                break
        if variable_name == '':
            raise RegexParserExpected("string", self.text, self.index)
        return variable_name
        