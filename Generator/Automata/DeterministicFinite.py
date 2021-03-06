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
import itertools
from ..CoverageSet import CoverageSet

class DeterministicState(object):
    """
    Represents a state in a deterministed finite automata (DFA)
    @ivar edges: dict representing a state transition table. 
        Keys are DeterministicState objects which represent destination states for an edge in the graph.
        Values are CoverageSet objects which representing the values which lead to the corresponding destination.
    @ivar is_final: boolean which is true if the state may be used as a final state
    @ivar ids: set of string with ids of possible rule matches in which this state could result.
    @ivar final_ids: if this is a final state, this field contains a set of strings with the ids of rules which were matched.
    """
    def __init__(self):
        # edges = dict(sink state -> edges leading to that state)
        self.edges = collections.defaultdict(CoverageSet)
        self.is_final = False
        self.ids = set()
        self.final_ids = set()
        
class DeterministicFinite(object):
    """
    Represents a deterministic finite automata (DFA). May be iterated to yield DeterministicState objects for each contained state.
    @ivar start_state: DeterministicState object representing the initial state
    """
    def __init__(self):
        self.start_state = None

    def __iter__(self):
        state_queue = collections.deque([self.start_state])
        visited = set([self.start_state])
        while len(state_queue) > 0:
            next_state = state_queue.pop()
            for destination in next_state.edges.iterkeys():
                if destination not in visited:
                    visited.add(destination)
                    state_queue.appendleft(destination)
            yield next_state

    def __repr__(self):
        """
        Returns a GraphViz(.dot) representation of the state machine
        """
        states = [state for state in self]
        start_state_index = states.index(self.start_state)
        
        descriptions = []
        descriptions.append('    %d [label="start", shape=none];' % len(states))
        for state in states:
            if len(state.ids) > 0 and not state.is_final:
                ids = [str(i) if i is not None else 'Anonymous' for i in state.ids]
                descriptions.append('    %d [label="%d\\n(%s)"];' % (states.index(state), states.index(state), ", ".join(ids)))
            elif len(state.final_ids) == 0 and state.is_final:
                descriptions.append('    %d [shape=octagon];' % (states.index(state)))
            elif len(state.final_ids) > 0 and state.is_final:
                ids = [str(i) if i is not None else 'Anonymous' for i in state.ids]
                final_ids = [str(i) if i is not None else 'Anonymous' for i in state.final_ids]
                descriptions.append('    %d [label="%d\\n(%s)\\n(%s)",shape=octagon];' % (states.index(state), states.index(state), ", ".join(ids), ", ".join(final_ids)))
            
        descriptions.append('    %d -> %d' % (len(states), start_state_index))
        
        for state in states:
            state_index = states.index(state)
            state_description = ""
            
            def format_codepoint(codepoint):
                if codepoint == ord('"'):
                    return "'\\\"'"
                if codepoint in xrange(32, 127):
                    return "'%s'" % chr(codepoint).replace("\\", "\\\\")
                else:
                    return "0x%x" % codepoint
            
            def format_case(range):
                if range[0] == range[1]:
                    return "%s" % format_codepoint(range[0])
                else:
                    return "%s-%s" % tuple([format_codepoint(i) for i in range])
            
            for destination, edges in state.edges.iteritems():
                edge_label = ", ".join([format_case(i) for i in edges])
                descriptions.append('    %d -> %d [label="%s"]' % (state_index, states.index(destination), edge_label))
           
        return "digraph {\n%s\n}\n" % "\n".join(descriptions)
    
    def copy(self):
        """
        Returns a copy of the DFA
        @return: an Automata.DeterministicFinite object which is equavalent to this object.
        """
        new_states = dict([(state, DeterministicState()) for state in self])
        for state in self:
            new_states[state].is_final = state.is_final
            new_states[state].ids = state.ids
            new_states[state].final_ids = state.final_ids
            for destination, edges in state.edges.iteritems():
                new_states[state].edges[new_states[destination]].update(edges)
        self_copy = DeterministicFinite()
        self_copy.start_state = new_states[self.start_state]
        return self_copy
        
    def reverse(self):
        """
        Returns a reverse of the DFA, which is an NFA that starts at each end state of the DFA, and transitions towards the initial state.
        @return: an Automata.NonDeterministicFinite object containing the reverse of the DFA.
        """
        nfa_state_machine = NonDeterministicFinite()
        
        # First convert to an NFA by copying states and linking to start/end state
        for dfa_state in self:
            dfa_state.nfa_proxy = NonDeterministicState()
            dfa_state.nfa_proxy.is_one_to_many_proxy = False
            if dfa_state == self.start_state:
                dfa_state.nfa_proxy.epsilon_edges.add(nfa_state_machine.end_state)
            if dfa_state.is_final:
                nfa_state_machine.start_state.epsilon_edges.add(dfa_state.nfa_proxy)
            
        # Copy edges with the direction reversed
        for dfa_state in self:
            for edge in dfa_state.edges:
                source_nfa_state = dfa_state.edges[edge].nfa_proxy
                if edge not in source_nfa_state.edges:
                    source_nfa_state.edges[edge] = set()
                source_nfa_state.edges[edge].add(dfa_state.nfa_proxy)
    
        return nfa_state_machine

    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __eq__(self, other):
        # Iterate both DFAs simultaneously, return false if something doesn't match
        state_map = {self.start_state: other.start_state}
        state_queue = collections.deque([(self.start_state, other.start_state)])

        while len(state_queue) > 0:
            self_state, other_state = state_queue.pop()
            if len(self_state.edges) != len(other_state.edges):
                return False
            for self_destination, self_edge in self_state.edges.iteritems():
                if self_destination in state_map:
                    # We have visited this destination - Make sure edges leading to it are identical
                    other_destination = state_map[self_destination]
                    if other_destination not in other_state.edges:
                        return False
                    if other_state.edges[other_destination] != self_edge:
                        return False
                else:
                    # We have not visited this destination - Search for matching edge in other DFA
                    other_destination = None
                    for possible_destination, other_edge in other_state.edges.iteritems():
                        if (other_edge == self_edge and 
                            frozenset(self_destination.final_ids) == frozenset(possible_destination.final_ids) and
                            self_destination.is_final == possible_destination.is_final):
                            state_map[self_destination] = possible_destination
                            other_destination = possible_destination
                            break
                    if other_destination is None:
                        return False
                    state_queue.appendleft((self_destination, other_destination))    
        return True
        