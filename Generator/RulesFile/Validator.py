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
from Visitor import Visitor

class Validator(Visitor):
    """
    Visitor class to objects in the rules file AST, to flatten the section
    hierarchy and check for duplicate names
    """
    def __init__(self):
        Visitor.__init__(self)
        self.rules = {}
        self.sections = {}
        self.defines = {}
        
    def visit_rule(self, rule):
        if rule.id.lower() in self.rules:
            rule.throw("duplicate rule ID '%s'" % rule.id)
        self.rules[rule.id.lower()] = rule
            
    def visit_reserved_id(self, reserved_id):
        if reserved_id.id.lower() in self.rules:
            rule.throw("duplicated reserved ID '%s'" % rule.id)
        self.rules[reserved_id.id.lower()] = None
        
    def visit_define(self, define):
        define_id = self.traverser.get_scoped_id(define.id)
        if define_id in self.defines:
            define.throw("duplicate variable ID '%s'" % define.id)
        self.defines[define_id] = define
    
    def visit_section(self, section):
        section_id = self.traverser.get_scoped_id(section.id)
        if section_id in self.sections:
            section.throw("duplicate section ID '%s'")
        self.sections[section_id] = section
        self.section_name = section.id

    def leave_section(self, section):
        current_section_id = self.traverser.get_scoped_id(section.id)
        if len(current_section_id) > 0:
            current_section = self.sections[current_section_id]
            if len(current_section.rules) == 0:
                current_section.throw("no rules in section '%s'" % section.id)
