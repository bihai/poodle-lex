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
from LexicalAnalyzerVisitor import LexicalAnalyzerVisitor

class LexicalAnalyzerValidator(LexicalAnalyzerVisitor):
    """
    Visitor class to objects in the LexicalAnalyzerAST, to resolve section
    references and check for duplicate names
    """
    def __init__(self):
        LexicalAnalyzerVisitor.__init__(self)
        self.rules = {}
        self.sections = {}
        self.defines = {}
        
    def visit_rule(self, rule):
        if rule.id.lower() in self.rules:
            rule.throw("Duplicate rule ID '%s'" % rule.id)
        self.rules[rule.id.lower()] = rule
            
    def visit_reserved_id(self, reserved_id):
        if reserved_id.id.lower() in self.rules:
            rule.throw("Duplicated reserved ID '%s'" % rule.id)
        self.rules[reserved_id.id.lower()] = None
        
    def visit_define(self, define):
        define_id = self.traverser.get_scoped_id(define.id)
        if define_id in self.sections:
            define.throw("Duplicate variable ID '%s'" % define.id)
        self.defines[define_id] = define
    
    def visit_section(self, section):
        section_id = self.traverser.get_scoped_id(section.id)
        if section_id in self.sections:
            section.throw("Duplicate section ID '%s'")
        self.sections[section_id] = section
