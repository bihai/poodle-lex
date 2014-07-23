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

import unittest
import sys
import os.path
sys.path.append(os.path.join("..", ".."))
from Generator.RulesFile.AST import *
from Generator.RulesFile.Visitor import Visitor

class TestResolvedSectionComparer(Visitor):
    def __init__(self, other, rule_id, section_id):
        self.other = other
        self.rule_id = rule_id
        self.section_id = section_id
        
        self.type = None
        self.other_type = None
        self.message = ""
        self.other_message = ""
        
    @staticmethod
    def compare(lhs, rhs, rule_id, section_id):
        comparer = TestResolvedSectionComparer(rhs, rule_id, section_id)
        lhs.accept(comparer)
        
    def visit_section(self, section):
        message = "section {id}".format(section.id)
        type = "section"
        if section == self.other:
            self.other_message = message
            self.other_type = type
            self.check_objects(section)
        else:
            self.message = message
            self.type = type
            self.other.accept(self)
            
    def visit_section_reference(self, section_reference):
        message = "section {id} by reference".format(section_reference.name)
        type = "section reference"
        if section_reference == self.other:
            self.other_message = message
            self.other_type = type
            self.check_objects(section_reference)
        else:
            self.message = message
            self.type = type
            self.other.accept(self)
            
    def check_objects(self, ast_object):
        if self.type != self.other_type:
            self.throw()
        if self.type == "section reference":
            if ast_object.name.lower() != self.other.name.lower():
                self.throw()
        elif self.type == "section":
            try:
                TestASTComparer.compare(ast_object, self.other)
            except Exception:
                self.throw(ast_object)

    def throw(self):
        raise Exception("In section {section_id}, rule {id} enters {message}, but in the other object it enters {other_message}".format(
            section_id = self.section_id,
            id = self.rule_id,
            message = self.message,
            other_message = self.other_message))
                
class TestASTComparer(Visitor):
    def __init__(self, other):
        self.current_section = None
        self.other_section = None
        self.other = other
        self.other_pattern = None
        
    @staticmethod
    def compare(lhs, rhs):
        comparer = TestASTComparer(rhs)
        lhs.accept(comparer)
        
    def find(resource, ast_object):
        candidates = self.other_section.find(resource.lower(), ast_object.id)
        if len(candidates) == 0:
            raise Exception("{resource} {id} not found in section {parent} of the other object".format(
                resource=resource,
                id=ast_object.id, 
                parent=self.other_section.id))
        other = candidates[0]
            
    @staticmethod
    def format_does(value):
        return "does" if value else "does not"
        
    def visit_section(self, section):
        if self.other_section is None:
            other = self.other
        else:
            other = self.find('Section', section)
        
        if section.inherits != other.inherits:
            raise Exception("Section {id} {section_does} inherit, but in the other object it {other_does}".format(
                id = section.id,
                section_does = self.format_does(section.inherits),
                other_does = self.format_does(other.inherits)))

        # Same set of children?
        all_children = set()
        all_children.update(section.children)
        all_children.update(other.children)
        for child in all_children:
            if child not in other.children:
                raise Exception("Section {id} contains a child scope {child_id}, but in the other object it does not".format(
                    id=section.id,
                    child_id=child))
            elif child not in section.children:
                raise Exception("Section {id} in the other object contains a child scope {child_id}, but in this object it does not".format(
                    id=section.id,
                    child_id=child))
                    
        self.current_section = section
        self.other_section = section
        
    def leave_section(self, section):
        self.current_section = section.parent
        self.other_section = self.other_section.parent
                
    def visit_rule(self, rule):
        other = self.find('Rule', rule.id)
        
        try:
            self.other_pattern = other.pattern
            rule.pattern.accept(self)
            
            if set(other.rule_action) != set(rule.rule_action):
                raise Exception("this has rules {action}, but in the other object it has rules {other_action}".format(
                    id=rule.id,
                    section_id=self.current_section.id,
                    action=rule.rule_action,
                    other_action=rule.section_action))
                    
            if rule.section_action is None and other.section_action is not None:
                raise Exception("this does not have an action regarding section, but in the other object it does".format(
                    id = rule.id,
                    section_id = self.current_section.id))
            elif rule.section_action is not None and other.section_action is None:
                raise Exception("this has an action regarding section, but in the other object it does not".format(
                    id = rule.id,
                    section_id = self.current_section.id))
            elif rule.section_action is not None:
                action, section = rule.section_action
                other_action, other_section = other.section_action
                if other_action != action:
                    raise Exception("this has a section action of {action}, but in the other object it has a section action of {other_action}".format(
                        action = action,
                        other_action = other_action))
                if action == 'enter':
                    TestResolvedSectionComparer.compare(section, rule.id, self.current_section.id)
        except Exception as e:
            raise Exception("In rule {id} in section {section_id}, {message}".format(
                id = rule.id,
                section_id = self.current_section.id, 
                message = e.message))
            
    def visit_define(self, define):
        other = self.find('Define', define.id)
        self.other_pattern = other.pattern
        try:
            define.pattern.accept(self)
        except Exception as e:
            raise Exception("In define {id} in section {section_id}, {message}".format(
                id = define.id,
                section_id = self.current_section.id, 
                message = e.message))
        
    def visit_pattern(self, pattern):
        if pattern.regex != self.other_pattern.regex:
            raise Exception("pattern regex does not match regex in other object")
        if pattern.is_case_insensitive != self.othe_pattern.is_case_insensitive:
            raise Exception("pattern's case sensitivity does not match the other object")
        
                
                
        
