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

import itertools
from ...CoverageSet import CoverageSet

def pair_id(i, j):
    """
    Sorts a pair of number so that the smaller number is first and the larger is second
    @param i: an integer representing a state
    @param j: an integer representing a state
    """
    return (min(i, j), max(i, j))

def minimize(state_machine):
    """
    Minimizes a deterministic finite automata (DFA) graph using an O(n^2) algorithm 
    which compares the distinctiveness of every pair of states. The automata passed 
    in is modified and nothing is returned.
    @param state_machine: an Automata.DeterministicFinite object representing the DFA to minimize.
    """   
    states = [state for state in state_machine]
    is_distinct = set()
    
    # Step 1: mark final/non-final pairs of states as distinct
    for i in range(len(states)):
        for j in range(i):
            if states[i].final_ids != states[j].final_ids:
                is_distinct.add(pair_id(i, j))
                
    # Step 2: compare destinations for each alphabet to determine that they are unique
    change_occurred = True
    while change_occurred:
        change_occurred = False
        for i in range(len(states)):
            for j in range(i):
                if pair_id(i, j) not in is_distinct:
                    all_edges = itertools.chain(states[i].edges.itervalues(), states[j].edges.itervalues())
                    for (min_v, max_v), ids in CoverageSet.segments(*((edge, index) for index, edge in enumerate(all_edges))):
                        destination_i = next((k for k, v in states[i].edges.iteritems() if min_v in v), None)
                        destination_j = next((k for k, v in states[j].edges.iteritems() if min_v in v), None)
                        
                        # States are distinct if alphabets not the same
                        if destination_i is None or destination_j is None:
                            is_distinct.add(pair_id(i, j))
                            change_occurred = True
                        else:
                            # States are distinct if they has an identical edges to distinct states
                            destination_index_i = states.index(destination_i)
                            destination_index_j = states.index(destination_j)
                            if pair_id(destination_index_i, destination_index_j) in is_distinct:
                                is_distinct.add(pair_id(i, j))
                                change_occurred = True

    # Step 3: Group non-distinct states
    non_distinct_pairs = set()
    for i in range(len(states)):
        for j in range(i):
            if pair_id(i, j) not in is_distinct:
                non_distinct_pairs.add(pair_id(i, j))
                
    non_distinct_groups = []
    for i, j in non_distinct_pairs:
        found = False
        for group in non_distinct_groups:
            if i in group or j in group:
                group.add(i)
                group.add(j)
                found = True             
        if not found:
            non_distinct_groups.append(set([i, j]))
   
    # Step 4: Merge non-distinct states
    state_to_merged = {}
    for i in xrange(len(non_distinct_groups)):
        non_distinct_groups[i] = list(non_distinct_groups[i])
    for group in non_distinct_groups:
        for state_index, state in [(i, states[i]) for i in group]:
            state_to_merged[state] = states[group[0]]
    for state in states:
        if state not in state_to_merged:
            state_to_merged[state] = state
    for group in non_distinct_groups:
        to_merge = [states[i] for i in group[1:]]
        merge_into = states[group[0]]
        for state in to_merge:
            for destination, edge in state.edges.iteritems():
                merge_into.edges[state_to_merged[destination]].update(edge)
        for edge in merge_into.edges.itervalues():
            edge.remove_overlap()
        for state in states:
            for destination in state.edges.keys():
                if destination in to_merge:
                    state.edges[merge_into].update(state.edges[destination])
                    del state.edges[destination]
        if state_machine.start_state in to_merge:
            state_machine.start_state = merge_into
