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
import Regex
import copy
import string

class NonDeterministicFiniteAutomataBuilder(object):
    """
    Visitor object which converts a regular expression into a non-deterministic finite automata (NFA) graph. 
    """
    def __init__(self, id):
        self.state_machines = []
        self.id = id
    
    def visit_literal(self, literal):
        """
        Converts a regular expression literal into an NFA with a transition for each contained character.
            Pushes the NFA onto a stack.
        @param literal: a Regex.Literal object representing the literal to convert.
        """
        state_machine = Automata.NonDeterministicFiniteAutomata()
        state_machine.start_state.edges[state_machine.end_state].update(literal.characters)
        self.state_machines.append(state_machine)
 
    def visit_literal_except(self, literal_except):
        """
        Converts a regular expression inverse literal ([^...]) into an equivalent NFA.
            Pushes the NFA onto a stack.
        @param literal: a Regex.LiteralExcept object representing the inverse literal to convert.
        """
        state_machine = Automata.NonDeterministicFiniteAutomata()
        state_machine.start_state.edges[state_machine.end_state].add(1, 0x10FFFF)
        state_machine.start_state.edges[state_machine.end_state].difference_update(literal_except.characters)
        self.state_machines.append(state_machine)        
 
    def visit_repetition(self, repetition):
        """
        Converts a repeated regular exprsesion into an equivalent NFA.
            Pushes the NFA onto a stack.
        @param repetition: a Regex.Repetition object representing the repeated expression to convert.
        """
        state_machine = None
        repetition.child.accept(self)
        child_state_machine = self.state_machines.pop()
        
        # Create optional 0 to max-min
        repetition_min = repetition.min
        if repetition.max == Regex.Repetition.Infinity:
            # Kleene star
            inner_state_machine = copy.deepcopy(child_state_machine)
            state_machine = Automata.NonDeterministicFiniteAutomata()
            state_machine.start_state.epsilon_edges.add(inner_state_machine.start_state)
            inner_state_machine.end_state.epsilon_edges.add(state_machine.end_state)
            inner_state_machine.end_state.epsilon_edges.add(inner_state_machine.start_state)
            if repetition.min == 0:
                state_machine.start_state.epsilon_edges.add(state_machine.end_state)
            else:
                repetition_min -= 1
            
        elif repetition.max > repetition_min:
            state_machines = [copy.deepcopy(child_state_machine) for i in xrange(repetition.max - repetition_min)]
            for state_machine in state_machines:
                state_machine.start_state.epsilon_edges.add(state_machine.end_state)
            state_machine = Automata.NonDeterministicFiniteAutomata.concatenate(state_machines)
            
        # Prepend minimal repetition 
        if repetition_min > 0:
            head_state_machines = [copy.deepcopy(child_state_machine) for i in xrange(repetition_min)]
            head_state_machine = Automata.NonDeterministicFiniteAutomata.concatenate(head_state_machines)
            if state_machine is None:
                state_machine = head_state_machine
            else:
                state_machine = Automata.NonDeterministicFiniteAutomata.concatenate([head_state_machine, state_machine])
                
        self.state_machines.append(state_machine)
        
    def visit_concatentation(self, concatenation):
        """
        Converts a concatenated set of regular expressions into an equivalent NFA graph.
            Pushes the graph onto a stack.
        @param concatentation: a Regex.Concatenation object representing the set of concatenated expressions.
        """
        child_state_machines = []
        for child in concatenation.children:
            child.accept(self)
            child_state_machines.append(self.state_machines.pop())
        
        self.state_machines.append(Automata.NonDeterministicFiniteAutomata.concatenate(child_state_machines))
                
    def visit_alternation(self, alternation):
        """
        Converts an alternated (separated by "|") regular expressions into an equivalent NFA graph.
            Pushes the graph onto a stack.
        @param alternation: a Regex.Alternation object representing the set of alternated expressions.
        """
        child_state_machines = []
        for child in alternation.children:
            child.accept(self)
            child_state_machines.append(self.state_machines.pop())
        self.state_machines.append(Automata.NonDeterministicFiniteAutomata.alternate(child_state_machines))
    
    def get(self):
        """
        Returns the NFA graph for the top level regular expression visited by this object.
        @return: a NonDeterministicFiniteAutomata object representing the NFA.
        """
        if len(self.state_machines) > 0:
            for state in self.state_machines[0]:
                state.ids.add(self.id)
            self.state_machines[0].end_state.final_ids.add(self.id)
            return self.state_machines[0]
            
