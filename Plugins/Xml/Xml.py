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

from PluginTemplate import PluginTemplate
from EmitCode import CodeEmitter
from CachedFormatter import CachedFormatter
import xml.etree.ElementTree as ElementTree
from itertools import chain
import xml.dom.minidom

def create_emitter(rules_file, dependencies, plugin_options):
    return XmlPlugin(rules_file, dependencies, plugin_options)
    
def maybe(include, value_factory):
    if include:
        return [value_factory()]
    else:
        return []

def pretty_print(root, stream):
    flat = ElementTree.tostring(root, 'utf-8')
    parsed = xml.dom.minidom.parseString(flat)
    return parsed.writexml(stream, addindent="    ", newl='\n', encoding='utf-8')
        
class XmlPlugin(PluginTemplate):
    def __init__(self, rules_file, dependencies, plugin_options):
        self.rules_file = rules_file
        self.dependencies = dependencies
        self.plugin_options = plugin_options
        self.file_name = self.plugin_options.file_name
        if self.file_name is None:
            self.file_name = "LexicalAnalyzer"
        self.cache = CachedFormatter(limit=64, reserved=[])
        self.cache.add_cache('id', lambda id: id if id is not None else 'Anonymous', 'ids')
        self.cache.add_cache('rule', lambda id_and_rule: id_and_rule[1], 'ids')
        self.cache.add_cache('state', lambda state_and_name: state_and_name[1], 'ids')

    # PluginTemplate interface
    def process(self, token):
        if token.token == "ROOT":
            self.generate_root(token)
    
    def get_output_directories(self):
        return []
        
    def get_files_to_copy(self):
        return []
        
    def get_files_to_generate(self):
        return [("LexicalAnalyzer.xml", self.file_name + ".xml")]

    # Private utility methods
    def get_form(self):
        return "NFA"if self.plugin_options.form == self.plugin_options.NFA_IR else "DFA"

    @staticmethod
    def get_rules(ids, section):
        return (rule for rule in section.rules if rule.id in ids)
        
    @staticmethod
    def get_rule_name(rule):
        return 'Anonymous' if rule.name is None else rule.name
        
    @staticmethod
    def get_rule_names(ids, section):
        return (XmlPlugin.get_rule_name(rule) for rule in XmlPlugin.get_rules(ids, section))
        
    def format_state_id(self, state, section):
        return self.cache.get_state((state, ''.join(self.get_rule_names(state.ids, section))))
        
    def format_rule_id(self, rule, section):
        return self.cache.get_rule((rule.id, self.get_rule_name(rule)))
        
    # Generation methods
    def generate_root(self, token):
        E = self.dependencies["ElementTreeFactory"]._E()
        root = E.LexicalAnalyzer(
            E.Form(self.get_form()),
            E.Sections(*list(self.generate_sections(E))),
            xmlns="https://github.com/parkertomatoes/poodle-lex")
        pretty_print(root, token.stream)
            
    def generate_sections(self, E):
        for id, section in self.rules_file.sections.items():
            yield self.generate_section(E, id, section)
                
    def generate_section(self, E, id, section):
        def section_rules():
            return [E.Rules(*list(self.generate_rules(E, section)))]
        def section_state_machine():
            return self.generate_state_machine(E, section, section.dfa)
        def section_attributes():
            return {'id': self.cache.get_id(id), 'inherits': str(section.inherits).lower(), 'exits': str(section.exits).lower()}
        print list(rule.id for rule in section.rules)    
        return E.Section(
            *(section_rules() + maybe(hasattr(section, 'dfa'), section_state_machine)), 
            **section_attributes())
    
    def generate_rules(self, E, section):
        for rule in section.rules:
            yield self.generate_rule(E, section, rule)
            
    def generate_rule(self, E, section, rule):
        def rule_actions():
            return E.Actions(*(E.Action(action) for action in rule.action))
        def rule_section_action():
            return E.SectionAction(*list(
                [E.Action(rule.section_action[0])]  
                + maybe(rule.section_action[1] is not None, lambda: E.Section(rule.section_action[1]))
            ))
        def rule_nfa():
            return self.generate_state_machine(E, section, rule.nfa)
        def get_rule_id():
            return self.format_rule_id(rule, section)
        def get_rule_name():
            return self.get_rule_name(rule)
        def rule_attributes():
            if hasattr(rule, 'line_number'):
                return {'name': get_rule_name(), 'id': get_rule_id(), 'line_number': rule.line_number}
            else:
                return {'name': get_rule_name(), 'id': get_rule_id()}
        
        return E.Rule(*(
            maybe(any(rule.action), rule_actions)
            + maybe(
                rule.section_action is not None and rule.section_action[0] is not None,
                rule_section_action)
            + maybe(hasattr(rule, 'nfa'), rule_nfa)
        ), **rule_attributes())
        
    def generate_state_machine(self, E, section, state_machine):
        def state_machine_start_state():
            return self.format_state_id(state_machine.start_state, section)
        def state_machine_end_state():
            return self.format_state_id(state_machine.end_state, section)
        def state_machine_attributes():
            if hasattr(state_machine, 'end_state'):
                return {'start': state_machine_start_state(), 'end': state_machine_end_state()}
            else:
                return {'start': state_machine_start_state()}
            
        return E.StateMachine(
            *list(self.generate_states(E, section, state_machine)), 
            **state_machine_attributes()
        )
        
    def generate_states(self, E, section, state_machine):
        for state in state_machine:
            yield self.generate_state(E, section, state)

    def generate_state(self, E, section, state):
        return E.State(
            E.Ids(*self.generate_state_ids(E, section, state.ids)),
            E.FinalIds(*self.generate_state_ids(E, section, state.final_ids)),
            E.Transitions(*list(self.generate_transitions(E, section, state))),
            id=self.format_state_id(state, section)
        )

    def generate_state_ids(self, E, section, ids):
        for rule in self.get_rules(ids, section):
            yield E.Id(self.format_rule_id(rule, section))
        
    def generate_transitions(self, E, section, state):
        return chain(
            self.generate_edge_transitions(E, section, state),
            maybe(hasattr(state, 'epsilon_edges'), lambda: self.generate_epsilon_transitions(E, section, state))
        )
        
    def generate_edge_transitions(self, E, section, state):
        for destination, edge in state.edges.items():
            yield E.Transition(
                *list(self.generate_edge(E, section, state, destination, edge)),
                Destination=self.format_state_id(destination, section)
            )
            
    def generate_edge(self, E, section, state, destination, edge):
        for (minv, maxv) in edge:
            if minv == maxv:
                yield E.Codepoint(str(minv))
            else:
                yield E.Range(start=str(minv), end=str(maxv))
        
    def generate_epsilon_transitions(self, E, section, state):
        for destination in state.epsilon_edges:
            yield E.Transition(Destination=self.format_state_id(destination))
            