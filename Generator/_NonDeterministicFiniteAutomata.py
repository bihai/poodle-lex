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
import Automata
from CoverageSet import CoverageSet

class NonDeterministicState(object):
    """
    Represents a state in a non-deterministic finite automata (NFA)
    @ivar ids: set of strings with rule ids of possible matches to which this state could lead
    @ivar final_ids: set of strings which contain, if the state is an end state, rule ids of the matching rules.
    @ivar edges: dict representing a state transition table, with each item representing an edge in the graph.
        Keys are NonDeterministicFiniteState objects representing the destination state for an edge
        Values are CoverageSet objects representing the values which lead to the corresponding destination.
    @ivar epsilon: set of NonDeterministicState objects representing the destinations of epsilon edges eminating from this state.
    """
    def __init__(self):
        self.ids = set()
        self.final_ids = set()
        
        # edges = dict(edge -> set(sink states))
        self.edges = collections.defaultdict(CoverageSet)
        
        # epsilon_edges = set(sink states)
        self.epsilon_edges = set()
        
class NonDeterministicFiniteAutomata(object):
    """
    Represents a non-deterministic finite automata (NFA) graph. 
        This object may be iterated to yield NonDetermisticState objects for each contained state.
    @ivar start_state: NonDeterministicState object representing the initial state of the automata.
    @ivar end_state: NonDeterministicState object representing the final state of the automata. 
    """
    def __init__(self):
        self.start_state = NonDeterministicState()
        self.end_state = NonDeterministicState()

    def __iter__(self):
        state_queue = collections.deque([self.start_state])
        visited = set([self.start_state])
        while len(state_queue) > 0:
            next_state = state_queue.pop()
            for destination in next_state.epsilon_edges:
                if destination not in visited:
                    visited.add(destination)
                    state_queue.appendleft(destination)
            for destination in next_state.edges.iterkeys():
                if destination not in visited:
                    visited.add(destination)
                    state_queue.appendleft(destination)
                    
            yield next_state
        
    def __repr__(self):
        states = [state for state in self]
        start_state_index = states.index(self.start_state)
        end_state_index = states.index(self.end_state)
        
        descriptions = []
        descriptions.append('    %d [label="start", shape=none];' % len(states))
        descriptions.append('    %s [label="end", shape=none];' % (len(states)+1))
        for state in states:
            if len(state.ids) > 0:
                descriptions.append('    %d [label="%d\\n(%s)"];' % (states.index(state), states.index(state), ", ".join([i for i in state.ids])))
        descriptions.append('    %d -> %d' % (len(states), start_state_index))
        descriptions.append('    %d -> %d' % (end_state_index, len(states)+1))
        for state in states:
            state_index = states.index(state)
            state_description = ""
            if len(state.epsilon_edges) > 0:
                descriptions.extend([unicode('    %d -> %d [label="&epsilon;"]') % (state_index, states.index(i)) for i in state.epsilon_edges])

            def format_codepoint(codepoint):
                if codepoint == ord('"'):
                    return "'\\\"'"
                elif codepoint in xrange(32, 127):
                    return "'%s'" % chr(codepoint)
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

    @staticmethod
    def concatenate(state_machines):
        """
        Merges a list of state machines by concatenating one after the other.
            Effectively places an epsilon transition between the end state of each automata and the initial state of the next.
            State machines are consumed by this function and cannot be used afterwards.
        @param state_machines: An array of NonDeterministicFiniteAutomata objects representing the automata to be merged.
        @return: NonDeterministicFiniteAutomata object representing the merged state machines.
        """
        if len(state_machines) == 1:
            return state_machines[0]

        # Chain state machines with epsilons
        for i in xrange(len(state_machines)-1):
            for state in state_machines[i]:
                if state_machines[i].end_state in state.epsilon_edges:
                    state.epsilon_edges.remove(state_machines[i].end_state)
                    state.epsilon_edges.add(state_machines[i+1].start_state)
                discarded_states = set()
                new_edge = CoverageSet()
                for destination, edge in state.edges.iteritems():
                    if destination == state_machines[i].end_state:
                        discarded_states.add(destination)
                        new_edge.update(edge)
                state.edges[state_machines[i+1].start_state].update(new_edge)
                for discarded_state in discarded_states:
                    del state.edges[discarded_state]
        state_machines[0].end_state = state_machines[-1].end_state
        return state_machines[0]
    
    @staticmethod
    def alternate(state_machines):
        """
        Merges a list of state machines by alternating them. 
            Effectively creates a new initial state with epsilon edges to each automata'a initial state, 
            and a final state with epsilon edges from each automata's final state.
            State machines are consumed and cannot be used after calling this function
        @param state_machines: a list of NonDeterministicFiniteAutomata objects representing the state machines to be merged.
        @return: a NonDeterministicFiniteAutomata object representing the merged state machines.
        """
        alternated_state_machine = NonDeterministicFiniteAutomata()
        for state_machine in state_machines:
            alternated_state_machine.start_state.epsilon_edges.add(state_machine.start_state)
            state_machine.end_state.epsilon_edges.add(alternated_state_machine.end_state)
        return alternated_state_machine
