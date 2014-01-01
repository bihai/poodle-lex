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
import Automata
from DeterministicFiniteAutomataBuilder import DeterministicFiniteAutomataBuilder
import itertools

class DeterministicState(object):
    """
    Represents a state in a deterministed finite automata (DFA)
    @ivar edges: dict representing a state transition table. 
        Keys represent edges eminating from this class. 
        Values represent destination state for the edge
    @ivar is_final: boolean which is true if the state may be used as a final state
    @ivar ids: set of string with ids of possible rule matches in which this state could result.
    @ivar final_ids: if this is a final state, this field contains a set of strings with the ids of rules which were matched.
    """
    def __init__(self):
        # edges = dict(character -> sink state)
        self.edges = {}
        self.is_final = False
        self.ids = set()
        self.final_ids = set()
        
class DeterministicFiniteAutomata(object):
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
            for destination in next_state.edges.itervalues():
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
            if len(state.final_ids) > 0 and not state.is_final:
                descriptions.append('    %d [label="%d\\n(%s)"];' % (states.index(state), states.index(state), ", ".join([i for i in state.final_ids])))
            elif len(state.final_ids) == 0 and state.is_final:
                descriptions.append('    %d [shape=octagon];' % (states.index(state)))
            elif len(state.final_ids) > 0 and state.is_final:
                descriptions.append('    %d [label="%d\\n(%s)",shape=octagon];' % (states.index(state), states.index(state), ", ".join([i for i in state.final_ids])))
            
        for state in [i for i in states if i.is_final == True]:
            descriptions.append('    %d [shape=octagon];' % states.index(state))        
        
        descriptions.append('    %d -> %d' % (len(states), start_state_index))
        
        for state in states:
            state_index = states.index(state)
            state_description = ""
            
            def ranges(i):
                for a, b in itertools.groupby(enumerate(i), lambda (x, y): y - x):
                    b = list(b)
                    yield b[0][1], b[-1][1]
            
            def format_codepoint(codepoint):
                if codepoint == ord('"'):
                    return "'\\\"'"
                if codepoint in xrange(32, 127):
                    return "'%s'" % chr(codepoint)
                else:
                    return "0x%x" % codepoint
            
            def format_case(range):
                if range[0] == range[1]:
                    return "%s" % format_codepoint(range[0])
                else:
                    return "%s-%s" % tuple([format_codepoint(i) for i in range])
            
            # first, group edges by destination
            edge_groups = collections.defaultdict(list)
            for edge, destination in state.edges.iteritems():
                edge_groups[destination].append(edge)
            
            # for each group of edges, lump ranges (e.g. "1-4") together
            for destination, edges in edge_groups.iteritems():
                edge_codepoints = sorted([ord(edge) for edge in edges])
                edge_label = ", ".join([format_case(range) for range in ranges(edge_codepoints)])
                descriptions.append('    %d -> %d [label="%s"]' % (state_index, states.index(destination), edge_label))
           
        return "digraph {\n%s\n}\n" % "\n".join(descriptions)
    
    def minimize(self):
        """
        Minimizes the state machine using Brzozowski's method:
            1. Reverse the DFA into an NFA
            2. Convert back to DFA
            3. Reverse the DFA into an NFA again
            4. Convert back to a DFA
            This method minimizes the DFA, but does not preserve information about ids.
        @return: a DeterministicFiniteAutomata obect containing a minimized version of the DFA
        """
        reversed = self.reverse()
        reversed_dfa = DeterministicFiniteAutomataBuilder(reversed).get()
        double_reversed = reversed_dfa.reverse()
        return DeterministicFiniteAutomataBuilder(double_reversed).get()

    def copy(self):
        """
        Returns a copy of the DFA
        @return: a DeterministicFiniteAutomata object which is equavalent to this object.
        """
        new_states = dict([(state, DeterministicState()) for state in self])
        for state in self:
            new_states[state].is_final = state.is_final
            new_states[state].ids = state.ids
            new_states[state].final_ids = state.final_ids
            for edge, destination in state.edges.iteritems():
                new_states[state].edges[edge] = new_states[destination]
        self_copy = DeterministicFiniteAutomata()
        self_copy.start_state = new_states[self.start_state]
        return self_copy
        
    def reverse(self):
        """
        Returns a reverse of the DFA, which is an NFA that starts at each end state of the DFA, and transitions towards the initial state.
        @return: a NonDeterministicFiniteAutomata objct containing the reverse of the DFA.
        """
        nfa_state_machine = Automata.NonDeterministicFiniteAutomata()
        
        # First convert to an NFA by copying states and linking to start/end state
        for dfa_state in self:
            dfa_state.nfa_proxy = Automata.NonDeterministicState()
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
