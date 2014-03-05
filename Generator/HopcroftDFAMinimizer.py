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
import collections
from CoverageSet import CoverageSet
import pickle

class StateGroup(object):
    def __init__(self, items=[]):
        self.states = set(items)
        
    def add(self, item):
        self.states.add(item)

    def __contains__(self, item):
        return item in self.states
    
    def __iter__(self):
        return iter(self.states)
        
def minimize(state_machine):
    """
    Minimizes a deterministic finite automata (DFA) graph using Hopcroft's O(n*log(n)) 
        algorithm. The automata passed in is modified and nothing is returned.
    @param state_machine: a DeterministicFiniteAutomata object representing the DFA to minimize.
    """
    states = [state for state in state_machine]
    
    # Step 1: Partition based on final states
    group_map = collections.defaultdict(StateGroup)
    for state in states:
        group_map[hash(frozenset(state.final_ids))].add(state)
    distinct_groups = set(group_map.itervalues())
    
    # Step 2: Iteritively partition based the signals going out of each partition
    group_was_split = True
    u = 0
    while group_was_split:
        u += 1
        group_was_split = False
        groups_to_add = set()
        groups_to_delete = set()
        state_to_group = {}
        for group in distinct_groups:
            for state in group:
                state_to_group[state] = group
        for group in distinct_groups:
            new_groups = collections.defaultdict(StateGroup)
            for state in group:
                outgoing_edges = collections.defaultdict(CoverageSet)
                for destination, edge in state.edges.iteritems():
                    outgoing_edges[state_to_group[destination]].update(edge)
                new_groups[tuple(sorted(outgoing_edges.iteritems()))].add(state)
            if len(new_groups) > 1:
                groups_to_delete.add(group)
                groups_to_add.update(new_groups.itervalues())
        distinct_groups.difference_update(groups_to_delete)
        distinct_groups.update(groups_to_add)
        if len(groups_to_add) > 0:
            group_was_split = True
                
    # Step 3: Group non-distinct states
    for group_set in distinct_groups:
        group = list(group_set)
        if len(group) > 1:
            to_merge = group[1:]
            for state in group[1:]:
                for destination, edge in state.edges.iteritems():
                    group[0].edges[destination].update(edge)
            for edge in group[0].edges.itervalues():
                edge.remove_overlap()
            for state in states:
                for destination_state in state.edges.keys():
                    if destination_state in to_merge:
                        state.edges[group[0]].update(state.edges[destination_state])
                        del state.edges[destination_state]
            if state_machine.start_state in to_merge:
                state_machine.start_state = group[0]
