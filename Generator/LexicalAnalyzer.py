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

from RegexParser import RegexParser
from RegexExceptions import *
from NonDeterministicFiniteAutomataBuilder import NonDeterministicFiniteAutomataBuilder
from DeterministicFiniteAutomataBuilder import DeterministicFiniteAutomataBuilder
import NaiveDFAMinimizer
import Automata
import LexicalAnalyzerParser

class LexicalAnalyzerException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message
    def __repr__(self):
        return self.message

class Rule(object):
    """
    Represents a single rule with an id and a regular expression
    @ivar id: string which identifies the rule
    @ivar pattern: string representing the rule's regular expression pattern
    @ivar regex: an object from the Regex package representing the rule's regular expression pattern
    @ivar nfa: a non-deterministic finite automata representing the rule's regular expression pattern
    """
    def __init__(self, id, pattern, is_case_insensitive=False):
        """
        @param id: string containing the id of the rule
        @param pattern: string containing the regular expression pattern of the rule
        @param is_case_insensitive: boolean representing if the pattern is case insensitive
        """
        self.pattern = pattern
        self.id = id
        self.regex = RegexParser(pattern, is_case_insensitive).parse()
        nfa_visitor = NonDeterministicFiniteAutomataBuilder(id)
        self.regex.accept(nfa_visitor)
        self.nfa = nfa_visitor.get()

class LexicalAnalyzer(object):
    """
    Represents a lexical analyzer.
    @ivar rules: a list of tuple pairs, which each tuple pair representing a rule. 
        Each rule tuple contains a string for the rule id, and a Rule object representing the rule.
        The smaller the index of the rule, the higher priority the rule is.    
    
    """
    def __init__(self, rules=[]):
        self.rules = []
        for rule in rules:
            self.add_rule(rule[0], rule[1])
        self._finalized = False
        self._nfa = None
        self._dfa = None
        
    @staticmethod
    def parse(file):
        """
        Creates a lexical analyzer from a rules definition file
        @param file: string containing the file name of the rules definition file.
        """
        lexer = LexicalAnalyzer()
        for rule_id, pattern, is_case_insensitive in LexicalAnalyzerParser.parse(file):
            lexer.add_rule(rule_id, pattern, is_case_insensitive)
        return lexer

    def add_rule(self, id, pattern, is_case_insensitive=False):
        """
        Adds a rule to the lexical analyzer.
        @param id: string identifying the rule
        @param pattern: string containing the regular expression of the rule's pattern.
        @param is_case_insensitive: boolean which is true if the pattern should be case insensitive. Optional, false by default.
        """
        self.check_not_final()
        try:
            if id == '':
                raise Exception("Can't have empty rule")
                
            if id in [rule.id for rule in self.rules]:
                raise Exception("Duplicate rule: '%s'" % id)
            
            self.rules.append(Rule(id, pattern, is_case_insensitive))
        except RegexParserExceptionInternal as e:
            raise RegexParserException(id, e.message)
    
    def is_finalized(self):
        """
        @return: boolean which is true if lexical analyzer is finalized.
        """
        return self._finalized

    def finalize(self):
        """
        Finalizes the lexical analyzer. Should be called once the rules are all defined.
        """
        self.check_not_final()
        rule_nfas = [rule.nfa for rule in self.rules]
        self._nfa = Automata.NonDeterministicFiniteAutomata.alternate(rule_nfas)
        self._dfa = DeterministicFiniteAutomataBuilder(self._nfa).get()
        self._min_dfa = self._dfa.copy()
        NaiveDFAMinimizer.minimize(self._min_dfa)
        self._finalized = True
        
    def check_final(self):
        """
        Raises an exception if the lexical analyzer is not finalized"
        """
        if not self._finalized:
            raise LexicalAnalyzerException("Lexical analyzer must be finalized before automata")
            
    def check_not_final(self):
        """ 
        Raises an exception if the lexical analyer is finalized
        """
        if self._finalized:
            raise LexicalAnalyzerException("Action is not allowed once lexical analyzer is finalized")
        
    def get_dfa(self):
        """
        Gets the DFA representation fo the lexical analyzer.
        @return: a DeterministicFiniteAutomata object representing the lexical analyzer.
        """
        self.check_final()
        return self._dfa
        
    def get_min_dfa(self):
        """
        Gets the minimized DFA representation fo the lexical analyzer.
        @return: a minimized DeterministicFiniteAutomata object representing the lexical analyzer.
        """
        self.check_final()
        return self._min_dfa
    
    def get_nfa(self):
        """
        Gets the NFA from the lexical analyzer
        @return: a NonDeterministicFiniteAutomata object repesenting the lexical analyzer.
        """
        self.check_final()
        return self._nfa
        
    def export_nfa(self, file):
        """
        Write the NFA representation of the lexical analyzer to a GraphViz(.dot) file
        @param file: string containing the name of the file to which the NFA should be exported.
        """
        self.check_final()
        with open(file, 'w') as f:
            f.write(repr(self._nfa))
            
    def export_dfa(self, file):
        """
        Write the DFA representation of the lexical analyzer to a GraphViz(.dot) file
        @param file: string containing the name of the file to which the NFA should be exported.
        """
        self.check_final()
        with open(file, 'w') as f:
            f.write(repr(self._dfa))
    
    def export_min_dfa(self, file):
        """
        Write the minimized DFA representation of the lexical analyzer to a GraphViz(.dot) file
        @param file: string containing the name of the file to which the NFA should be exported.
        """
        self.check_final()
        with open(file, 'w') as f:
            f.write(repr(self._min_dfa))
    
    def export_rule_nfa(self, id, file):
        """
        Write the NFA representation of a rule in the lexical analyzer to a GraphViz(.dot) file
        @param id: string containing the id of the rule to export
        @param file: string containing the name of the file to which the NFA should be exported.
        """
        if id == '':
            raise LexicalAnalyzerException("Can't have empty rule")
        rules = [rule for rule in self.rules if rule.id == id]
        if len(rules) == 0:
            raise LexicalAnalyzerException("Rule not found: '%s'" % id)
        with open(file, 'w') as f:
            f.write(repr(rules[0].nfa))
        
