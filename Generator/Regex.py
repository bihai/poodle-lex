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

from CoverageSet import CoverageSet

class Literal(object):
    """
    Visitable regular expression object repesenting one or more characters
    @ivar characters: sting containing the characters represented by this expression.
    """
    def __init__(self, characters):
        """
        @param characters: sting containing the characters represented by this expression.
        """
        self.characters = CoverageSet(characters)

    def __repr__(self):
        return "Literal(%s)" % ", ".join(["%d-%d" % (m, n) for m, n in self.characters])
        
    def accept(self, visitor):
        visitor.visit_literal(self)
        
class LiteralExcept(object):
    """
    Visitable regular expression object representing "all except" one or more characters.
    @ivar characters: string containing the characters excluded by this expression.
    """
    def __init__(self, characters):
        """
        @param characters: string containing the characters excluded by this expression.
        """
        self.characters = CoverageSet(characters)        
 
    def __repr__(self):
        return "LiteralExcept(%s)" % ", ".join(["%d-%d" % (m, n) for m, n in self.characters])
 
    def accept(self, visitor):
        visitor.visit_literal_except(self)
        
class Alternation(object):
    """
    Visitable regular expression object representing an alternation (e.g. the "|" operator) of one or more sub-expressions
    @ivar children: a list containing visitable regular expression objects representing the alternated sub-expressions.
    """
    def __init__(self, children):
        """
        @param children: a list containing visitable regular expression objects representing the alternated sub-expressions.
        """
        self.children = children
        
    def __repr__(self):
        return "Alternation(%s)" % ", ".join([repr(i) for i in self.children])
        
    def accept(self, visitor):
        visitor.visit_alternation(self)
        
class Concatenation(object):
    """
    Visitable regular expression object representing a concatentation of one or more sub-expressions
    @ivar children: a list containing visitable regular expression objects representing the concatenated sub-expressions.
    """
    def __init__(self, children):
        """
        @param children: a list containing visitable regular expression objects representing the concatenated sub-expressions.
        """
        self.children = children
        
    def __repr__(self):
        return "Concatenation(%s)" % ", ".join([repr(i) for i in self.children])
        
    def accept(self, visitor):
        visitor.visit_concatentation(self)
        
class Repetition(object):
    """
    Visitable regular expression object representing a repeated sub-expression.
    @ivar child: visitable regular expression object representing the repeated sub-expression.
    @ivar min: integer representing the minimum number of times the sub-expression can repeat.
    @ivar max: integer representing the maximum number of times the sub-expression can repeat.
    """
    Infinity = -1
 
    def __init__(self, child, min, max):
        """
        @param child: a visitable regular expression object representing the repeated sub-expression.
        @param min: integer representing the minimum number of times the sub-expression can repeat.
        @param max: integer representing the maximum number of times the sub-expression can repeat.
        """
        self.child = child 
        self.min = min
        self.max = max
    
    def __repr__(self):
        min_text = str(self.min)
        if (self.min < 0):
            min_text = "inf"
        max_text = str(self.max)
        if (self.max < 0):
            max_text = "inf"
        return "Repetition(%s, %s, %s)" % (repr(self.child), min_text, max_text)
    
    def accept(self, visitor):
        visitor.visit_repetition(self)
 
