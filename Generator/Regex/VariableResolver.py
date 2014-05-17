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
from Exceptions import *

class VariableResolver(object):
    """
    Visitor object which copies a regular expression, except for variables. Variables are replaced with a regular expression found in defines.
    """
    def __init__(self, defines):
        self.defines = defines
        self.visited = set()
        self.stack = []
    
    def visit_literal(self, literal):
        new_literal = Regex.Literal([])
        new_literal.characters = literal.characters
        self.stack.append(new_literal)
        
    def visit_literal_except(self, literal_except):
        new_literal_except = Regex.LiteralExcept([])
        new_literal_except.characters = literal_except.characters
        self.stack.append(new_literal_except)
        
    def visit_repetition(self, repetition):
        new_repetition = Regex.Repetition(None, repetition.min, repetition.max)
        repetition.child.accept(self)
        new_repetition.child = self.stack.pop()
        self.stack.append(new_repetition)
        
    def visit_concatenation(self, concatenation):
        new_concatenation = Regex.Concatenation([])
        for child in concatenation.children:
            child.accept(self)
            new_concatenation.children.append(self.stack.pop())
        self.stack.append(new_concatenation)
            
    def visit_alternation(self, alternation):
        new_alternation = Regex.Alternation([])
        for child in alternation.children:
            child.accept(self)
            new_alternation.children.append(self.stack.pop())
        self.stack.append(new_alternation)
            
    def visit_variable(self, variable):
        """
        When visiting a variable, just visit the regular expression defined for that 
        variable. By visiting, we resolve all variables in the definition too. After 
        visiting, a resolved copy of the variable definition will be at the top of the stack.
        """
        if variable.name in self.visited:
            raise RegexParserCircularReference(variable.name)
        if variable.name not in self.defines:
            raise RegexParserUndefinedVariable(variable.name)
        self.visited.add(variable.name)
        self.defines[variable.name].accept(self)
        self.visited.remove(variable.name)
        
    def get(self):
        """
        Returns a copy of the 
        @return: an Automata.NonDeterministicFinite object representing the NFA.
        """
        return self.stack[-1]
