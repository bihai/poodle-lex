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

class Pattern(object):
    """
    Represents a regular expression string
    @ivar regex: string containing the regular expression
    @ivar is_case_insensitive: boolean which is true if the regular expression string should be case-insensitive
    """
    def accept(self, visitor):
        visitor.visit_pattern(self)

    def __init__(self, regex, is_case_insensitive):
        self.regex = regex
        self.is_case_insensitive = is_case_insensitive
    
    def __repr__(self):
        return "Pattern(%s, %s)" % (self.regex, self.is_case_insensitive)
        
class Define(object):
    """
    Represents a 'Let id = pattern' variable declaration
    @ivar id: the name of the variable 
    @ivar pattern: a Pattern object representing the variable's value
    """
    def accept(self, visitor):
        visitor.visit_define(self)
        
    def __init__(self, id, pattern):
        self.id = id
        self.pattern = pattern
        
    def __repr__(self):
        return "Define(%s, %s)" % (self.id, repr(self.pattern))

class SectionReference(object):
    """
    Represents an unresolved reference to a section
    @ivar name: the name of section being referenced
    """
    def accept(self, visitor):
        visitor.visit_section_reference(self)
        
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return "SectionReference(%s)" % self.name
        
class Rule(object):
    """
    Represents a lexical analyzer rule with a 'action? id: pattern (section_action section?)?' syntax
    @ivar id: string containing the name of the rule
    @ivar pattern: Pattern object representing the regular expression that matches the rule
    @ivar rule_action: string containing the action to take with the token matched by the rule
    @ivar section_action: string containing the action to take after matching the rule
    @ivar section: Section or SectionReference object specifying which section the analyzer should enter after matching the rule
    """
    def accept(self, visitor):
        visitor.visit_rule(self)

    def __init__(self, id, pattern, rule_action=None, section_action=None, section=None):
        self.id = id
        self.pattern = pattern
        self.rule_action = rule_action
        self.section_action = section_action
        self.section = section
        
    def __repr__(self):
        return "Rule(Id=%s, %s, Action=%s, SectionAction=%s, Section=%s)" % (repr(self.id), repr(self.pattern), repr(self.rule_action), repr(self.section_action), repr(self.section))
        
class Section(object):
    """
    Represents a grouping of rules, ids, and reserved keywords
    @ivar rules: list of Rule objects representing rules in the section, in order of priority
    @ivar defines: list of Define objects representing variable definitions in the section, in order of priority
    @ivar reserved_ids: list of strings representing reserved identifiers
    @ivar standalone_sections: list of sections not tied to a rule
    """
    def accept(self, visitor):
        visitor.visit_section(self)
        
    def __init__(self, id, rules=[], defines=[], reserved_ids=[], standalone_sections=[]):
        self.id = id
        self.rules = list(rules)
        self.defines = list(defines)
        self.reserved_ids = list(reserved_ids)
        self.standalone_sections = list(standalone_sections)
        
    def __repr__(self):
        rule_string = "Rules=[%s]" % ", ".join(repr(rule) for rule in self.rules)
        define_string = "Defines=[%s]" % ", ".join(repr(define) for define in self.defines)
        reserved_string = "Reserved=[%s]" % ", ".join(self.reserved_ids)
        section_string = "StandaloneSections=[%s]" % ", ".join(repr(section) for section in self.standalone_sections)
        return "Section(%s, %s, %s, %s, %s)" % (repr(self.id), rule_string, define_string, reserved_string, section_string)
