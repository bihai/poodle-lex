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
import textwrap

def create_emitter(rules_file, dependencies, plugin_options):
    return DotPlugin(rules_file, dependencies, plugin_options)

class DotPlugin(PluginTemplate):
    reserved_ids = ['strict', 'graph', 'digraph', 'node', 'edge', 'subgraph']

    def __init__(self, rules_file, dependencies, plugin_options):
        def formatter(id, prefix=''):
            if id is not None:
                path = id.split('.')
                for i in range(len(path)):
                    path[i] = path[i].lower().replace(':', '')
                if len(path) > 1:
                    return prefix + '_'.join(path[1:])
                else:
                    return prefix + 'main'
            return prefix + 'anonymous'
            
        def section_formatter(id):
            return formatter(id, 'cluster_')
    
        self.rules_file = rules_file
        self.dependencies = dependencies
        self.plugin_options = plugin_options
        self.file_name = self.plugin_options.file_name
        if self.file_name is None:
            self.file_name = "LexicalAnalyzer"
        self.cache = CachedFormatter(limit=64, reserved=self.reserved_ids)
        self.cache.add_cache('id', formatter, 'ids')
        self.cache.add_cache('section', section_formatter, 'ids')
        self.state_map = {}
        self.exit_vertices = {}
        self.entry_vertex = None

    # PluginTemplate interface
    def process(self, token):
        if token.token == "CONTENT":
            self.generate_content(token)
    
    def get_output_directories(self):
        return []
        
    def get_files_to_copy(self):
        return []
        
    def get_files_to_generate(self):
        return [("LexicalAnalyzer.dot", self.file_name + ".dot")]
        
    # Private methods
    def generate_content(self, token):
        code = CodeEmitter(token.stream)
        code.indent()
        
        # Generate the state machine factory
        self.get_state_machine = lambda section: section.dfa
        if self.plugin_options.form == self.plugin_options.NFA_IR:
            nfas = {}
            for section in self.rules_file.sections.values():
                nfas[section] = section.rules[0].nfa.alternate(rule.nfa for rule in section.rules)
            self.get_state_machine = lambda section: nfas[section]

        # Generate vertices
        for id, section in self.rules_file.sections.items():
            formatted_id = self.cache.get_section(id)
            with code.block("subgraph {0} {{".format(formatted_id), "}"):
                code.line('label="{0}"'.format(self.get_section_label(section, id)))
                self.generate_vertices(code, formatted_id, section)
        for vertex in self.exit_vertices.values():
            self.draw_vertex(code, id=vertex, label="exit section", is_shapeless=True)
        
        code.line()
        
        #Generate edges
        for id, section in self.rules_file.sections.items():
            formatted_id = self.cache.get_section(id)
            self.generate_edges(code, formatted_id, section)
            
    @staticmethod
    def get_section_label(section, id):
        attributes = []
        if section.inherits:
            attributes.append('inherits')
        elif section.exits:
            attributes.append('exits')
        if any(attributes):
            return "{0} ({1})".format(id, ','.join(attributes))
        else:
            return id
                
    @staticmethod
    def get_rule_ids(rules, ids):
        for rule in rules:
            if rule.id in ids:
                if rule.name is not None:
                    yield rule.name
                else:
                    yield 'Anonymous'
                    
    @staticmethod
    def get_matching_rule(rules, ids):
        return next((rule for rule in rules if rule.id in ids), None)
                    
    def allocate_vertex(self, state=None):
        key = state
        value = self.state_map.get(key)
        if value is None:
            value = len(self.state_map)
            if key == None:
                key = value
            self.state_map[key] = value
        return value
        
    @staticmethod
    def draw_vertex(code, id, label=None, ids=None, final_ids=None, is_final=False, is_shapeless=False):
        text_label = label
        if text_label is None:
            text_label = id
        if is_shapeless:
            code.line('{i} [label="{label}", shape=none];'.format(i=id, label=text_label))
        elif ids is not None and not is_final:
            code.line('{i} [label="({ids})"];'.format(i=id, label=text_label, ids=ids))
        elif final_ids is None and is_final:
            code.line('{i} [label="{label}", shape=octagon];'.format(i=id, label=text_label))
        elif final_ids is not None and is_final:
            code.line('{i} [label="({ids})\\n({final_ids})", shape=octagon];'.format(i=id, label=text_label, ids=ids, final_ids=final_ids))
            
    @staticmethod
    def draw_edge(code, start, end, label=None):
        if label is None:
            code.line('{0} -> {1}'.format(start, end))
        else:
            code.line('{0} -> {1} [label="{2}"]'.format(start, end, label))
             
    @staticmethod
    def format_codepoint(codepoint):
        if codepoint == ord('"'):
            return "'\\\"'"
        if codepoint in xrange(32, 127):
            return "'%s'" % chr(codepoint).replace("\\", "\\\\")
        else:
            return "0x%x" % codepoint
    
    @staticmethod
    def format_case(range):
        if range[0] == range[1]:
            return "%s" % DotPlugin.format_codepoint(range[0])
        else:
            return "%s-%s" % tuple([DotPlugin.format_codepoint(i) for i in range])
            
    def allocate_vertices(self, section, id, state_machine):
        for state in state_machine:
            self.allocate_vertex(state)
        if id == "cluster_main":
            self.entry_vertex = self.allocate_vertex()
        exit_vertex = None
        if any(rule for rule in section.rules if rule.section_action is not None and rule.section_action[0] == 'exit'):
            exit_vertex = self.allocate_vertex()
            self.exit_vertices[id] = exit_vertex
    
    def generate_vertices(self, code, id, section):
        state_machine = self.get_state_machine(section)
        self.allocate_vertices(section, id, state_machine)
        
        for state in state_machine:
            i = self.state_map[state]
            ids = None
            if any(state.ids):
                ids = ', '.join(self.get_rule_ids(section.rules, state.ids))
            final_ids = None
            if any(state.final_ids):
                final_ids = ', '.join(self.get_rule_ids(section.rules, state.final_ids))
            self.draw_vertex(code, id=i, ids=ids, final_ids=final_ids, is_final=any(state.final_ids))
        if self.entry_vertex is not None:
            self.draw_vertex(code, id=self.entry_vertex, label="start", is_shapeless=True)
            
    def generate_edges(self, code, id, section):
        state_machine = self.get_state_machine(section)
        
        if self.entry_vertex is not None and id == 'cluster_main':
            self.draw_edge(code, self.entry_vertex, self.state_map[state_machine.start_state])
            
        for state in state_machine:
            for destination, edge in state.edges.items():
                edge_label = ", ".join([self.format_case(i) for i in edge])
                edge_label = '\\n'.join(textwrap.wrap(edge_label, 256))
                self.draw_edge(code, self.state_map[state], self.state_map[destination], edge_label)
                
            if hasattr(state, 'epsilon_edges'):
                for destination in state.epsilon_edges:
                    self.draw_edge(code, self.state_map[state], self.state_map[destination], '&epsilon;')
                
            if any(state.final_ids):
                rule = self.get_matching_rule(section.rules, state.final_ids)
                if rule is not None and rule.section_action is not None and rule.section_action[0] is not None:
                    label = rule.section_action[0]
                    destination = None
                    if rule.section_action[0] == 'exit':
                        destination = self.exit_vertices[id]
                    elif rule.section_action[0] in ('enter', 'switch'):
                        destination_section = self.rules_file.sections[rule.section_action[1]]
                        destination = self.get_state_machine(destination_section).start_state
                        if destination not in self.state_map:
                            self.allocate_vertex(destination)
                        destination = self.state_map[destination]
                    if destination is not None:
                        self.draw_edge(code, self.state_map[state], destination, label)
                        