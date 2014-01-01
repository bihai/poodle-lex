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

import Automata

class EpsilonClosureCrawler(object):
    """
    Class which, given a set of NFA states, can be used to find the epsilong closure of those states, 
        which is all the states reachable through epsilong edges.
    """
    def __init__(self, nfa_state_set):
        self.states = []
        for nfa_state in nfa_state_set:
            self.crawl(nfa_state)
    
    def crawl(self, nfa_state):
        """
        Recursively searches for states reachable through epsilon edges and appends them to an internal list.
        @nfa_state: NonDeterministicState object representing the start from which to start searching
        """
        self.states.append(nfa_state)
        for epsilon_destination in nfa_state.epsilon_edges:
            if epsilon_destination not in self.states:
                self.crawl(epsilon_destination)

    def get_states(self):
        """
        Returns the states found through epsilong closure.
        @return: array of NonDeterministicState objects containing the results of the search.
        """
        return self.states

class DeterministicFiniteAutomataBuilder(object):
    """
    Creates a deterministic finite automata (DFA) from a non-deterministic finite automata (NFA) via epsilon closure.
    """
    def __init__(self, nfa_state_machine):
        """
        @param nfa_state_machine: a NonDeterministicFiniteAutomata object representing the NFA to convert to a DFA
        """
        self.states = {}
        self.nfa_state_machine = nfa_state_machine
        self.dfa_state_machine = Automata.DeterministicFiniteAutomata()
        nfa_start_state = set([nfa_state_machine.start_state])
        nfa_start_state_closed = EpsilonClosureCrawler(nfa_start_state).get_states()
        dfa_start_state_id = frozenset(nfa_start_state_closed)
        self.states[dfa_start_state_id] = Automata.DeterministicState()
        for nfa_state in nfa_start_state_closed:
            self.states[dfa_start_state_id].ids.update(nfa_state.ids)
            self.states[dfa_start_state_id].final_ids.update(nfa_state.final_ids)
        self.dfa_state_machine.start_state = self.states[dfa_start_state_id]
        self.crawl(dfa_start_state_id)
        
    def crawl(self, state_id):
        """
        Crawls through the NFA, finding a unique list of epsilon closures for each states. This is done by:
            1. Creates a DFA state for each unique set of NFA states and store internally
            2. For each unique set, find an epsilon-closed set of all NFA states reachable for a given edge
            3. Map the destination state sets found in #2 to DFA states created in #1, and create the DFA state transition table.
        @param state_id: list of NFA states from which to crawl.
        """
        # Each DFA state is equivalent to a set of NFA states.
        # Any DFA state containing the NFA's end state is an end state
        if self.nfa_state_machine.end_state in state_id:
            self.states[state_id].is_final = True
            
        # Find possible edges
        edge_set = set()
        for nfa_state in state_id:
            edge_set.update(set(nfa_state.edges.keys()))
        
        # To find the destination state for each edge:
        # 1) Get a set of destination NFA state for that edge in each NFA state in the DFA state
        # 2) Find the epsilon closure for that set of NFA states.
        for edge in edge_set:
            destination_nfa_states = set()
            for nfa_state in state_id:
                if edge in nfa_state.edges:
                    destination_nfa_states.update(nfa_state.edges[edge])
            destination_state_id = frozenset(EpsilonClosureCrawler(destination_nfa_states).get_states())
            
            if destination_state_id not in self.states:
                self.states[destination_state_id] = Automata.DeterministicState()
                for nfa_state in destination_state_id:
                    self.states[destination_state_id].ids.update(nfa_state.ids)
                    self.states[destination_state_id].final_ids.update(nfa_state.final_ids)
                self.crawl(destination_state_id)
            
            self.states[state_id].edges[edge] = self.states[destination_state_id]
                
    def get(self):
        """
        Return the DFA created from the NFA passed into __init__
        @return: a DetermintisticFiniteAutomata object representing the DFA converted from the NFA passed into __init__
        """
        return self.dfa_state_machine
