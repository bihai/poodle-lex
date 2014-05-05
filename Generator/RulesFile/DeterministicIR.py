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
from ..DeterministicFiniteAutomataBuilder import DeterministicFiniteAutomataBuilder
from .. import Automata

class Section(object):
    """
    Represents a section in the intermediate representation. 
    @ivar dfa: A DeterministicFinite Object representing the state machine of rule-set
    @ivar priority: A list of strings, each the ID of a rule, in order of priority, with the highest first
    """
    def accept(self, visitor):
        visitor.visit_section(self)
    
    def __init__(self, dfa, priority):
        self.dfa = dfa
        self.priority = priority 
        
class Rule(object):
    """
    Represents meta-data for a rule, including ID, action, and section
    @ivar id: String containing the rule's identifier
    @ivar action: string containing the action to take with the rule
    @ivar section_action: tuple of a string a Section object. The string is the
        action to take on the current section, either None, 'enter', or 'exit'.
        If the action is 'enter', the Section object is the section to 
        enter. Otherwise, the Section object is None.
    """
    def accept(self, visitor):
        visitor.visit_rule(self)
    
    def __init__(self, id, action, section_action):
        self.id = id
        self.action = action
        self.section_action = section_action

class DeterministicIR(object):
    """
    Represents a lexical analyzer that has been reduced to deterministic
    finite automata.
    @ivar rules: A list of Rule objects representing metadata for each rule
    @ivar sections: A list of Section objects representing state machines for each section
    """
    def __init__(self, non_deterministic_ir):
        self.rules = {}
        self.sections = {}
        for id, section in non_deterministic_ir.sections.items():
            all_nfas = []
            priority = []
            for rule in section.rules:
                all_nfas.append(rule.nfa)
                self.rules[rule.id] = Rule(rule.id, rule.action, rule.section_action)
                priority.append(rule.id)
            combined_nfa = Automata.NonDeterministicFiniteAutomata.alternate(all_nfas)
            dfa = DeterministicFiniteAutomataBuilder(combined_nfa).get()
            self.sections[id] = Section(dfa, priority)
