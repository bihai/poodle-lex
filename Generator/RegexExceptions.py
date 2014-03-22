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

class RegexParserExceptionInternal(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message
        
    def __repr__(self):
        return str(self)

class RegexParserException(Exception):
    def __init__(self, rule_id, message, type='rule'):
        self.rule_id = rule_id
        self.message = message
        self.type = type
        
    def __str__(self):
        return "Error parsing %s '%s': %s" % self.type, self.rule, self.message
    
    def __repr__(self):
        return str(self)

class RegexParserExpected(RegexParserExceptionInternal):
    def __init__(self, expected, text, index):
        if index < len(text):
            self.message = u"Character %d: Expected \"%s\", found \"%s\"" % (index, expected, text[index])
        else:
            self.message = u"Expected \"%s\", but reached end of stream" % expected
            
class RegexParserUnicodeCodepointOutOfRange(RegexParserExceptionInternal):
    def __init__(self, codepoint):
        self.message = u"Unicode codepoint out of range: '%06x'" % codepoint
            
class RegexParserInvalidCharacterRange(RegexParserExceptionInternal):
    def __init__(self, min, max):
        self.message = u"Invalid Range: [%s-%s]" % (unicode(min), unicode(max))
        
class RegexParserInvalidCharacter(RegexParserExceptionInternal):
    def __init__(self, character):
        self.message = u"Invalid Character: '%s'" % unicode(character)

class RegexParserCircularReference(RegexParserExceptionInternal):
    def __init__(self, name):
        self.message = u"Circular reference to variable '%s' not allowed" % name
        
class RegexParserUndefinedVariable(RegexParserExceptionInternal):
    def __init__(self, name):
        self.message = u"Variable '%s' not defined" % name