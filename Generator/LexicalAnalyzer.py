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
import LexicalAnalyzerParser
import NaiveDFAMinimizer
import HopcroftDFAMinimizer
import Automata

class LexicalAnalyzerException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message
    def __repr__(self):
        return self.message
        
class Pattern(object):
    def __init__(self, pattern, is_case_insensitive=False):
        self.pattern = pattern
        self.is_case_insensitive = is_case_insensitive
        
    def get_regex(self):
        return RegexParser(self.pattern, self.is_case_insensitive).parse()
        
class Rule(object):
    """
    Represents a single rule with an id and a regular expression
    @ivar id: string which identifies the rule
    @ivar pattern: string representing the rule's regular expression pattern
    @ivar regex: an object from the Regex package representing the rule's regular expression pattern
    """
    _valid_actions = set(['skip', 'capture', 'reserve'])
    
    def __init__(self, id, pattern, action=None):
        """
        @param id: string containing the id of the rule
        @param pattern: string containing the regular expression pattern of the rule
        @param action: string containing a command to associate with the rule, or None
        """
        self.id = id
        self.pattern = pattern
        self.action = action
        if action is not None and action.lower() not in Rule._valid_actions:
            raise RegexParserException(id, "Action '%s' not suppported" % action)
            
    def __eq__(self, other_rule):
        same_id = self.id == other_rule.id
        same_pattern = repr(self.pattern) == repr(other_rule.pattern)
        same_action = self.action == other_rule.action
        return same_id and same_pattern and same_action
        
    def get_nfa(self, defines={}):
        """
        Convert the pattern for this rule into a new NFA
        @param defines: a dict mapping strings representing variable names to an object in the 
            Regex namespace, for variable substitution
        @return: a NonDeterministicFiniteAutomata object which represents the NFA equivalent of the rule's pattern
        """
        nfa_visitor = NonDeterministicFiniteAutomataBuilder(self.id, defines)
        self.pattern.accept(nfa_visitor)
        return nfa_visitor.get()
 
class LexicalAnalyzer(object):
    """
    Represents a lexical analyzer.
    @ivar rules: a list of tuple pairs, which each tuple pair representing a rule. 
        Each rule tuple contains a string for the rule id, and a Rule object representing the rule.
        The smaller the index of the rule, the higher priority the rule is.    
    """
    def __init__(self, rules=[], defines={}, minimizer=HopcroftDFAMinimizer.minimize):
        """
        @param rules: a list of tuple pairs, which contain a string containing the name of the rule, and a Pattern object containing the regular expression of the rule. 
        @param defines: a dictionary mapping strings represeneting names of substitutable variables to strings representing patterns which substitute them.
        @param minimizer: function which minimizes a given DeterministicFiniteAutomata object. Hopcroft's algorithm by default
        """
        self.reserved_ids = set()
        self.rules = []
        for rule in rules:
            self.add_rule(rule[0], rule[1])
        self.defines = {}
        for define_name, define_value in defines.iteritems():
            self.add_define(define_name, define_value)
        self._finalized = False
        self._nfa = None
        self._dfa = None
        self._minimizer = minimizer
        
    @staticmethod
    def parse(file, encoding, minimizer=HopcroftDFAMinimizer.minimize):
        """
        Creates a lexical analyzer from a rules definition file
        @param file: string containing the file name of the rules definition file.
        @param minimizer: function which minimizes a given DeterministicFiniteAutomata object. Hopcroft algorithm by default.
        """
        lexer = LexicalAnalyzerParser.LexicalAnalyzerParser(file, encoding).parse()
        lexer._minimizer = minimizer
        return lexer
        
    def reserve_id(self, id):
        """
        Reserves a token name for custom use
        @param id: string containing the rule id to reserve
        """
        if id in [rule.id for rule in self.rules] or id in self.reserved_ids:
            raise RegexParserException(id, "Id is already reserved: '%s'" % id)
        self.reserved_ids.add(id)

    def add_rule(self, id, pattern, action=None):
        """
        Adds a rule to the lexical analyzer.
        @param id: string identifying the rule
        @param pattern: Pattern object containing the regular expression of the rule's pattern.
        @param action string containing the action which should be take for the rule
        """
        self.check_not_final()
        try:
            if id == '':
                raise Exception("Can't have empty rule")
                
            if id in [rule.id for rule in self.rules] or id in self.reserved_ids:
                raise Exception("Duplicate rule: '%s'" % id)
            
            self.rules.append(Rule(id, pattern, action))
        except RegexParserExceptionInternal as e:
            raise RegexParserException(id, e.message)

    def add_define(self, id, pattern):
        """
        Adds a definition for a substitutable variable 
        @param id: string identifying the varaible
        @param pattern: Pattern object containing the regular expression of the rule's pattern.
        """
        self.check_not_final()
        try:
            if id == '':
                raise Exception("Can't have empty variable")
                
            if id in self.defines:
                raise Exception("Duplicate variable definition: '%s'" % id)
            
            self.defines[id] = pattern
        except RegexParserExceptionInternal as e:
            raise RegexParserException(id, e.message, type='variable definition')
            
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
        rule_nfas = []
        for rule in self.rules:
            try:
                rule_nfas.append(rule.get_nfa(self.defines))
            except RegexParserExceptionInternal as e:
                raise RegexParserException(rule.id, e.message)
        rule_nfas = [rule.get_nfa(self.defines) for rule in self.rules]
        self._nfa = Automata.NonDeterministicFiniteAutomata.alternate(rule_nfas)
        self._dfa = DeterministicFiniteAutomataBuilder(self._nfa).get()
        self._min_dfa = self._dfa.copy()
        self._minimizer(self._min_dfa)
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
        @return: a NonDeterministicFiniteAutomata object representing the lexical analyzer.
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
        