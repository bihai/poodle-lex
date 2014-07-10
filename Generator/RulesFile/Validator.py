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
import collections
import traceback

from Visitor import Visitor

class Validator(Visitor):
    """
    Visitor class to objects in the rules file AST, to flatten the section
    hierarchy and check for duplicate names
    @ivar future_imports: dictionary mapping reserved IDs to rules which import from them. Contains imports for reservations which have not been found at the time of processing
    """
    def __init__(self):
        Visitor.__init__(self)
        self.rule_ids = set()
        self.sections = {}
        self.defines = {}
        self.current_section = None
        
    def visit_rule(self, rule):
        rule_actions = rule.rule_action = [i.lower() for i in rule.rule_action]
        rule_id = rule.id.lower() if rule.id is not None else None

        # Check for bad command combinations
        valid_rule_actions = set(('skip', 'reserve', 'import', 'capture'))
        for action in rule_actions:
            if action not in valid_rule_actions:
                rule.throw("unrecognized action '{0}'".format(action))
        if rule.id == None and rule_actions != ['skip']:
            rule.throw("anonymous rules may only be skipped")
        if 'skip' in rule_actions and 'capture' in rule_actions:
            rule.throw("rule cannot both be skipped and captured")
        if 'reserve' in rule_actions and len(rule_actions) > 1:
            rule.throw("rule reservation cannot be mixed with other actions")
        if rule.pattern == None and 'import' not in rule_actions and 'reserve' not in rule_actions:
            rule.throw("rules not being either reserved or imported must have a pattern")
            
        if rule_id in self.rule_ids and 'import' not in rule_actions and rule_id is not None:
            rule.throw("duplicate rule ID '%s'" % rule.id)
        self.rule_ids.add(rule_id)
        
        # Resolve import or queue for later resolution
        if 'import' in rule_actions:
            reservation = self.current_section.find('reservation', rule_id)
            if reservation is None:
                self.current_section.add('future_import', rule)
            elif rule.pattern is None:
                if reservation[0].pattern is None:
                    rule.throw('pattern must be defined for imported rule if not defined by reservation rule')
                rule.pattern = reservation[0].pattern
            
        # Book reservation
        if 'reserve' in rule_actions:
            self.current_section.add('reservation', rule)
    
        
    def visit_define(self, define):
        define_id = self.traverser.get_scoped_id(define.id)
        if define_id in self.defines:
            define.throw("duplicate variable ID '%s'" % define.id)
        self.defines[define_id] = define
    
    #logger = logging.getLogger("joe")
    def visit_section(self, section):
        section_id = self.traverser.get_scoped_id(section.id)
        if section_id in self.sections:
            section.throw("duplicate section ID '%s'" % section.id)
        self.sections[section_id] = section
        self.current_section = section

    def leave_section(self, section):
        self.current_section = section.parent
        if len(section.all('rule')) == 0:
            section.throw("no rules in section '%s'" % section.id)
