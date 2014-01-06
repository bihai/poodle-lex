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
from CoverageSet import CoverageSet

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
    @param state_machine: a DeterministicFiniteAutomata object representing the DFA to minimize.
    """
    states = [state for state in state_machine]
    is_distinct = set()
    
    # Step 1: mark final/non-final pairs of states as distinct
    for i in range(len(states)):
        for j in range(i):
            if pair_id(i, j) not in is_distinct:
                if states[i].final_ids != states[j].final_ids:
                    is_distinct.add(pair_id(i, j))
                    
    # Step 2: compare destinations for each alphabet to determine that they are unique
    change_occurred = True
    while change_occurred:
        change_occurred = False
        for i in range(len(states)):
            for j in range(i):
                if pair_id(i, j) not in is_distinct:
                    # States are distinct if alphabets not the same
                    if set(states[i].edges.itervalues()) != set(states[j].edges.itervalues()):
                        is_distinct.add(pair_id(i, j))
                        change_occurred = True
                        continue
                        
                    # States are distinct if each has an identical edge to distinct states
                    for destination, edge in states[i].edges.iteritems():
                        destination_i = states.index(destination)
                        destination_j = states.index(next(k for k, v in states[j].edges.iteritems() if v == edge))
                        if pair_id(destination_i, destination_j) in is_distinct:
                            is_distinct.add(pair_id(i, j))
                            change_occurred = True
                            break
    
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
                group.append(i)
                group.append(j)
                found = True             
        if not found:
            non_distinct_groups.append([i, j])
   
    # Step 4: Merge non-distinct states
    for group in non_distinct_groups:
        if states.index(state_machine.start_state) in group:
            state_machine.start_state = states[group[0]]
        for state in states:
            duplicate_destinations = set()
            new_edge = CoverageSet()
            has_edge_to_group = False
            for destination_state, edge in state.edges.iteritems():
                if states.index(destination_state) in group:
                    new_edge.update(edge)
                    has_edge_to_group = True
                    if destination_state != states[group[0]]:
                        duplicate_destinations.add(destination_state)
            for destination in duplicate_destinations:
                del state.edges[destination]
            if has_edge_to_group:
                state.edges[states[group[0]]].update(new_edge)
            
                    
