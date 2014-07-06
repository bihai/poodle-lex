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

class Pattern(Node):
    """
    Represents a regular expression string
    @ivar regex: string containing the regular expression
    @ivar is_case_insensitive: boolean which is true if the regular expression string should be case-insensitive
    @ivar line_number: integer with the line number in the source where this object was parsed
    """
    def accept(self, visitor):
        visitor.visit_pattern(self)

    def __init__(self, regex, is_case_insensitive=False, line_number=None):
        self.regex = regex
        self.is_case_insensitive = is_case_insensitive
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
        
class SectionBase(Node):
    """
    Common interface for resolving both SectionReference and Section into a Section object
    """
    def get_section(self, scope):
        """
        Get a resolved Section object represented by this object
        @param scope: Scope object which contains
        @return: Section object represented by this object
        """
        return None

class SectionReference(SectionBase):
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
        
    def get_section(self, scope):
        result = scope.find('section', self.name)
        if result is None or len(result) == 0:
            self.throw("unknown section '%s'" % self.name)
        return result[0]
        
class Rule(Node):
    """
    Represents a lexical analyzer rule with a 'action? id: pattern (section_action section?)?' syntax
    @ivar id: string containing the name of the rule
    @ivar pattern: Pattern object representing the regular expression that matches the rule
    @ivar rule_action: string containing the action to take with the token matched by the rule
    @ivar section_action: string containing the action to take after matching the rule
    @ivar section: Section or SectionReference object specifying which section the analyzer should enter after matching the rule
    @ivar line_number: integer with the line number in the source where this object was parsed
    """
    def accept(self, visitor):
        visitor.visit_rule(self)

    def __init__(self, id, pattern, rule_action=[], section_action=None, line_number=None):
        self.id = id
        self.pattern = pattern
        self.rule_action = list(rule_action)
        self.section_action = section_action
        self.line_number = line_number
        
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
        
    def __eq__(self, rhs):
        self_icase_rule_action = [i.lower() for i in self.rule_action]
        rhs_icase_rule_action = [i.lower() for i in rhs.rule_action]
        return (isinstance(rhs, Rule) and
            Node.compare_nullable_icase(self.id, rhs.id) and
            self.pattern == rhs.pattern and
            self_icase_rule_action == rhs_icase_rule_action and
            self.section_action == rhs.section_action)
        
    def __repr__(self):
        return "Rule(Id=%s, %s, Action=%s, SectionAction=%s)" % (repr(self.id), repr(self.pattern), repr(self.rule_action), repr(self.section_action))
        
class Section(Scope):
    """
    Represents a grouping of rules, ids, and reserved keywords
    @ivar rules: list of Rule objects representing rules in the section, in order of priority
    @ivar defines: list of Define objects representing variable definitions in the section, in order of priority
    @ivar standalone_sections: list of sections not tied to a rule
    @iver inherits: True if this section should fall back on its parent's rules, False otherwise
    @ivar line_number: integer with the line number in the source where this object was parsed
    """
    def accept(self, visitor):
        visitor.visit_section(self)
        
    def __init__(self, id, parent=None, inherits=False, line_number=None, **resources):
        Scope.__init__(self, parent, line_number, **resources)
        self.id = id
        self.inherits = inherits
        self.line_number = line_number
        for id, section in self.all('section'):
            section.parent = self
            self.children[id.lower()] = section
        for id, rule in self.all('rule'):
            if rule.section_action is not None:
                action, target = rule.section_action
                if isinstance(target, Section):
                    self.add('section', target)
                    target.parent = self
            
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
        
    def __eq__(self, rhs):
        return (isinstance(rhs, Section) and
            Node.compare_nullable_icase(self.id, rhs.id) and
            self.inherits == rhs.inherits and
            Scope.__eq__(self, rhs))
        
    def __repr__(self):
        resources = []
        for resource_type in self.resources:
            formatted_type = resource_type.title()
            contents = ', '.join(repr(i) for i in self.resources[resource_type].values())
            resources.append('{type}=[{contents}]'.format(type=formatted_type, contents=contents))
        return "Section({id}, {resources}, Inherits={inherits})".format(
            id=repr(self.id), 
            resources=resources,
            inherits=self.inherits)

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