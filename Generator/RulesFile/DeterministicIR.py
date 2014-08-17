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

from .. import Automata
from ..Automata import Minimizer

class DeterministicIR(object):
    """
    Represents a lexical analyzer that has been reduced to deterministic
    finite automata.
    @ivar rule_ids: A set of strings, each containing the name of a possible rule. 
        This includes rules IDs which are reserved but not implemented
    @ivar sections: A dictionary with each string key being a section's 
        identifier, of Section objects representing state machines for each section
    """

    class Section(object):
        """
        Represents a section in the intermediate representation. 
        @ivar dfa: A DeterministicFinite Object representing the state machine of rule-set
        @ivar rules: A list of rule objects, in order of priority, containing meta data for each rule ID in order of priority
        @ivar inherits: True if the state machine should fall back to the parent's state machine if the state machine is
            put into an error state on the first character
        @ivar exits: True if the state machine should return to the parent's state machine if the state machine is
            put into an error state on the first character
        @ivar parent: String containing a qualified section ID of the section's hierarchical parent
        """
        def accept(self, visitor):
            visitor.visit_section(self)
        
        def __init__(self, dfa, rules, inherits, exits, parent):
            self.dfa = dfa
            self.rules = rules
            self.inherits = inherits
            self.exits = exits
            self.parent = parent
            
        def get_matching_rule(self, state):
            """
            Given a state, return the highest priority rule which can end in that state
            @param state: A DeterministicState object which exists within the section's DFA
            """
            return next((rule for rule in self.rules if rule.id in state.final_ids), None)
            
    class Rule(object):
        """
        Represents meta-data for a rule, including ID, action, and section
        @ivar id: String containing the rule's identifier
        @ivar action: list of actions for the rule to take
        @ivar section_action: tuple with two items. The first describes which action
            to take regarding the current section location upon matching the rule, and 
            can be either None, 'enter', or 'exit'. If the action is 'enter', the second
            item is a string representing the name of the section to enter. Otherwise, 
            the second item is None
        """
        def accept(self, visitor):
            visitor.visit_rule(self)
        
        def __init__(self, name, id, action, section_action):
            self.name = name
            self.id = id
            self.action = action
            self.section_action = section_action
            
        def has_action(self, action):
            return action in self.action

    def __init__(self, non_deterministic_ir, minimizer=Minimizer.hopcroft):
        self.rule_ids = dict(non_deterministic_ir.rule_ids)
        self.sections = {}
        for id, section in non_deterministic_ir.sections.items():
            section_nfas = []
            section_rules = []
            for rule in section.rules:
                section_nfas.append(rule.nfa)
                section_rules.append(DeterministicIR.Rule(rule.name, rule.id, rule.action, rule.section_action))
            combined_nfa = Automata.NonDeterministicFinite.alternate(section_nfas)
            dfa = Automata.DeterministicFiniteBuilder.build(combined_nfa)
            minimizer.__call__(dfa)
            self.sections[id] = DeterministicIR.Section(dfa, section_rules, section.inherits, section.exits, section.parent)
            
        
            
            