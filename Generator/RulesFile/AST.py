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

from Lexer import RulesFileException
from ASTBase import Node, Scope
from ..Common import lower_nullable

class PatternAttributes(object):
    """
    Represents the attributes which can be applied to a pattern using a 
    prefix attached to the first string. (e.g. i"hello")
    @ivar is_literal: Indicates that all characters in the pattern are literal
    @ivar is_unicode_defaults: Indicates that special characters and classes should use Unicode equivalents
    @ivar is_case_insensitive: Indicates that letters in the pattern should match both their uppercase and lowercase versions
    """
    def __init__(self, is_case_insensitive, is_unicode_defaults, is_literal):
        """
        @param is_literal: Boolean which, if True, indicates that all characters in the pattern are literal
        @param is_unicode_defaults: Boolean which, if True, indicates that special characters and classes should use Unicode equivalents
        @param is_case_insensitive: Boolean which, if True, indicates that letters in the pattern should match both their uppercase and lowercase versions
        """
        if is_literal and is_unicode_defaults:
            raise ValueError("Pattern cannot be both literal and have Unicode special characters")
        
        self.is_literal = is_literal
        self.is_unicode_defaults = is_unicode_defaults
        self.is_case_insensitive = is_case_insensitive

class Pattern(Node):
    """
    Represents a regular expression string
    @ivar regex: string containing the regular expression
    @ivar attributes: a set of pattern attributes which guide parsing
    @ivar line_number: integer with the line number in the source where this object was parsed
    """
    def accept(self, visitor):
        visitor.visit_pattern(self)

    def __init__(self, regex, attributes = PatternAttributes(False, False, False), line_number=None):
        self.regex = regex
        self.attributes = attributes
        self.line_number = line_number

    def __ne__(self, rhs):
        return not self.__eq__(rhs)
    def __eq__(self, rhs):
        return (isinstance(rhs, Pattern) and
            self.regex == rhs.regex and
            self.is_case_insensitive == rhs.is_case_insensitive)
    
    def __repr__(self):
        return "Pattern(\"%s\", %s)" % (self.regex, self.is_case_insensitive)
        
class Define(Node):
    """
    Represents a 'Let id = pattern' variable declaration
    @ivar id: the name of the variable 
    @ivar pattern: a Pattern object representing the variable's value
    @ivar line_number: integer with the line number in the source where this object was parsed
    """
    def accept(self, visitor):
        visitor.visit_define(self)
        
    def __init__(self, id, pattern, line_number=None):
        self.id = id
        self.pattern = pattern
        self.line_number = line_number
        
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
        
    def __eq__(self, rhs):
        return (isinstance(rhs, Define) and
            self.id.lower() == rhs.id.lower() and 
            self.pattern == rhs.pattern)
        
    def __repr__(self):
        return "Define(%s, %s)" % (repr(self.id), repr(self.pattern))
        
class SectionReference(Node):
    """
    Represents an unresolved reference to a section
    @ivar name: the name of section being referenced
    @ivar line_number: integer with the line number in the source where this object was parsed
    """
    def accept(self, visitor):
        visitor.visit_section_reference(self)
        
    def __init__(self, name, line_number=None):
        self.name = name
        self.line_number = line_number
        
    def __repr__(self):
        return "SectionReference(%s)" % repr(self.name)
        
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
        
    def __eq__(self, rhs):
        return self.name.lower() == rhs.name.lower()
        
class Rule(Node):
    """
    Represents a lexical analyzer rule with a 'action? id: pattern (section_action section?)?' syntax
    @ivar id: string containing the name of the rule
    @ivar pattern: Pattern object representing the regular expression that matches the rule
    @ivar rule_action: set of lowercase strings indicating what action to take if the rule matches
    @ivar section_action: string containing the action to take after matching the rule
    @ivar section: Section or SectionReference object specifying which section the analyzer should enter after matching the rule
    @ivar line_number: integer with the line number in the source where this object was parsed
    """
    def accept(self, visitor):
        visitor.visit_rule(self)

    def __init__(self, id, pattern, rule_action=[], section_action=None, line_number=None):
        self.id = id
        self.pattern = pattern
        self.rule_action = list(i.lower() for i in rule_action)
        if section_action is None:
            self.section_action = (None, None)
        else:
            self.section_action = section_action
        self.line_number = line_number
        
    def __hash__(self):
        return hash((lower_nullable(self.id), frozenset(self.rule_action), self.section_action))
        
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
        
    def __eq__(self, rhs):
        return (isinstance(rhs, Rule) and
            compare_nullable_icase(self.id, rhs.id) and
            self.pattern == rhs.pattern and
            self.rule_action == rhs.rule_action and
            self.section_action == rhs.section_action)
        
    def __repr__(self):
        return "Rule(Id=%s, %s, Action=%s, SectionAction=%s)" % (repr(self.id), repr(self.pattern), repr(self.rule_action), repr(self.section_action))
        
class Section(Scope):
    """
    Represents a grouping of rules, ids, and reserved keywords
    @ivar id: string which identifies the section within its containing scope
    @iver inherits: True if this section should fall back on its parent's rules, False otherwise
    @iver exits: True if this section should fall back on its parent's rules and exit the section if it does so, False otherwise
    @ivar line_number: integer with the line number in the source where this object was parsed
    """
    def accept(self, visitor):
        visitor.visit_section(self)
        
    def __init__(self, id, parent=None, inherits=False, exits=False, line_number=None, **resources):
        Scope.__init__(self, parent, line_number, **resources)
        self.id = id
        self.inherits = inherits
        self.exits = exits
        self.line_number = line_number
        for id, section in self.all('section'):
            section.parent = self
            self.children[id.lower()] = section
        for id, rule in self.all('rule'):
            action, target = rule.section_action
            if isinstance(target, Section):
                self.add('section', target)
                target.parent = self
                if target.id is not None:
                    self.children[target.id.lower()] = target
            
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
        
    def __eq__(self, rhs):
        return (isinstance(rhs, Section) and
            compare_nullable_icase(self.id, rhs.id) and
            self.inherits == rhs.inherits and
            self.exits == rhs.exits and
            Scope.__eq__(self, rhs))
        
    def __repr__(self):
        resources = []
        for resource_type in self.resources:
            formatted_type = resource_type.title()
            contents = ', '.join(repr(i) for i in self.resources[resource_type].values())
            resources.append('{type}=[{contents}]'.format(type=formatted_type, contents=contents))
        return "Section({id}, {resources}, Inherits={inherits}, Exits={exits})".format(
            id=repr(self.id), 
            resources=resources,
            inherits=self.inherits,
            exits=self.exits)

    def get_qualified_name(self):
        """
        Return the qualified (hierarchical) name of the section.
        @return: string representing the qualified name of the section
        """
        current_scope = self
        qualified_name_items = []
        while current_scope is not None:
            qualified_name_items.insert(0, current_scope)
            current_scope = current_scope.parent
                
        return '.'.join(i.id for i in qualified_name_items)