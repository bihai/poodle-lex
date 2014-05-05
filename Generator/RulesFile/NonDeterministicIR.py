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

from Visitor import Visitor, ScopedId, Traverser
from .. import Automata
from ..RegexParser import RegexParser
from ..NonDeterministicFiniteAutomataBuilder import NonDeterministicFiniteAutomataBuilder

class Section(object):
    """
    Represents a section in the intermediate representation
    """
    def __init__(self, rules=[]):
        self.rules = list(rules)
    
class Rule(object):
    """
    Represents a rule in the intermediate representation
    """
    def __init__(self, id, nfa, action, section_action, line_number):
        self.id = id
        self.nfa = nfa
        self.action = action
        self.section_action = section_action
        self.line_number = line_number
            
class NonDeterministicIR(object):
    def __init__(self, root, defines, sections):
        builder = NonDeterministicIR.Builder(defines, sections)
        traverser = Traverser(builder)
        root.accept(traverser)
        self.sections = builder.get()
        self.root = root
    
    class Builder(Visitor):
        """
        Visitor which constructs a NonDeterministicIR object from an
        AST node.
        """
        def __init__(self, defines, sections):
            self.all_defines = defines
            self.ast_sections = sections
            self.all_sections = dict((section, Section()) for section in sections)
            self.visible_defines = None
            self.visible_sections = None
            self.current_section = None
        
        def visit_section(self, section):
            """
            Update the scope upon visiting a section
            """
            self.visible_defines = {}
            self.visible_sections = {}
            if section is not None:
                self.current_section = self.traverser.get_scoped_id(section.id)
            else:
                self.current_section = self.traverser.get_scoped_id()
            for i in range(1, len(self.current_section)+1):
                for key, value in self.ast_sections.items():
                    if key in ScopedId(self.current_section[:i]):
                        self.visible_sections[key[-1]] = self.all_sections[key]
                for key, value in self.all_defines.items():
                    if key in ScopedId(self.current_section[:i]):
                        self.visible_defines[key[-1]] = self.all_defines[key]
                        
        def leave_section(self):
            """
            Update the scope upon leaving a section
            """
            self.visit_section(None)
        
        def visit_rule(self, rule):
            try:
                """
                Resolve section references and variables, compile the rule
                into an NFA, and add to the currently visited section.
                """
                regex = RegexParser(rule.pattern.regex, rule.pattern.is_case_insensitive).parse()
                nfa_builder = NonDeterministicFiniteAutomataBuilder(rule.id, self.visible_defines)
                regex.accept(nfa_builder)
                nfa = nfa_builder.get()
                section_action = None
                if rule.section_action is not None:
                    action, section = rule.section_action
                    if section is not None:
                        section = section.get_section(self.visible_sections)
                    section_action = (action, section)
                ir_rule = Rule(rule.id, nfa, rule.rule_action, section_action, rule.line_number)
                self.all_sections[self.current_section].rules.append(ir_rule)
                    
            except Exception as e:
                rule.throw("rule '%s': %s" % (rule.id, str(e)))
        
        def get(self):
            return self.all_sections
