import sys
sys.path.append("..")
import unittest
from Generator import Automata
from Generator.CoverageSet import CoverageSet
from Generator import NaiveDFAMinimizer
from Generator import HopcroftDFAMinimizer
from Generator.LexicalAnalyzer import LexicalAnalyzer

class TestDFAMinimization(unittest.TestCase):
    def test_minimization_simple(self):
        dfa = Automata.DeterministicFiniteAutomata()
        states = [Automata.DeterministicState() for i in xrange(9)]
        states[0].edges[states[1]] = CoverageSet([(1, 1)])
        states[0].edges[states[2]] = CoverageSet([(2, 2)])
        states[0].edges[states[3]] = CoverageSet([(3, 3)])
        states[1].edges[states[4]] = CoverageSet([(1, 3)])
        states[2].edges[states[4]] = CoverageSet([(1, 3)])
        states[3].edges[states[4]] = CoverageSet([(1, 3)])
        states[4].edges[states[5]] = CoverageSet([(1, 1)])
        states[4].edges[states[6]] = CoverageSet([(2, 2)])
        states[4].edges[states[7]] = CoverageSet([(3, 3)])
        states[5].edges[states[8]] = CoverageSet([(1, 3)])
        states[6].edges[states[8]] = CoverageSet([(1, 3)])
        states[7].edges[states[8]] = CoverageSet([(1, 1)])
        dfa.start_state = states[0]
        states[8].is_final = True
        states[8].final_ids = set(['Final'])
        NaiveDFAMinimizer.minimize(dfa)
        
        min_dfa = Automata.DeterministicFiniteAutomata()
        min_states = [Automata.DeterministicState() for i in xrange(6)]
        min_states[0].edges[min_states[1]] = CoverageSet([(1, 3)])
        min_states[1].edges[min_states[2]] = CoverageSet([(1, 3)])
        min_states[2].edges[min_states[3]] = CoverageSet([(1, 2)])
        min_states[2].edges[min_states[4]] = CoverageSet([(3, 3)])
        min_states[3].edges[min_states[5]] = CoverageSet([(1, 3)])
        min_states[4].edges[min_states[5]] = CoverageSet([(1, 1)])
        min_dfa.start_state = min_states[0]
        min_states[5].is_final = True
        min_states[5].final_ids = set(['Final'])
        
        self.assertEqual(dfa, min_dfa)
        
    def test_minimization_complex(self):
        dfa = Automata.DeterministicFiniteAutomata()
        states = [Automata.DeterministicState() for i in xrange(8)]
        states[0].edges[states[1]] = CoverageSet([(1, 1)])
        states[0].edges[states[2]] = CoverageSet([(0, 0)])
        states[1].edges[states[0]] = CoverageSet([(1, 1)])
        states[1].edges[states[2]] = CoverageSet([(0, 0)])
        states[2].edges[states[3]] = CoverageSet([(0, 1)])
        states[3].edges[states[4]] = CoverageSet([(0, 0)])
        states[3].edges[states[6]] = CoverageSet([(1, 1)])
        states[4].edges[states[6]] = CoverageSet([(0, 0)])
        states[4].edges[states[7]] = CoverageSet([(1, 1)])
        states[5].edges[states[6]] = CoverageSet([(1, 1)])
        states[5].edges[states[4]] = CoverageSet([(0, 0)])
        states[6].edges[states[6]] = CoverageSet([(0, 1)])
        states[7].edges[states[6]] = CoverageSet([(1, 1)])
        states[7].edges[states[7]] = CoverageSet([(0, 0)])
        dfa.start_state = states[0]
        states[6].is_final = True
        states[6].final_ids = set(['Final'])
        states[7].is_final = True
        states[7].final_ids = set(['Final'])
        dfa_copy = dfa.copy()
        
        NaiveDFAMinimizer.minimize(dfa)
        HopcroftDFAMinimizer.minimize(dfa_copy)
        
        min_dfa = Automata.DeterministicFiniteAutomata()
        min_states = [Automata.DeterministicState() for i in xrange(5)]
        min_states[0].edges[min_states[0]] = CoverageSet([(1, 1)])
        min_states[0].edges[min_states[1]] = CoverageSet([(0, 0)])
        min_states[1].edges[min_states[2]] = CoverageSet([(0, 1)])
        min_states[2].edges[min_states[3]] = CoverageSet([(0, 0)])
        min_states[2].edges[min_states[4]] = CoverageSet([(1, 1)])
        min_states[3].edges[min_states[4]] = CoverageSet([(0, 1)])
        min_states[4].edges[min_states[4]] = CoverageSet([(0, 1)])
        min_dfa.start_state = min_states[0]
        min_states[4].is_final = True
        min_states[4].final_ids = set(['Final'])
        
        self.assertEqual(dfa, min_dfa)
        self.assertEqual(dfa, dfa_copy)

    def test_complex_dfa_minimization_case(self):
        NaiveLexer = LexicalAnalyzer.parse("TestDFAMinimization.rules", "utf8", minimizer=NaiveDFAMinimizer.minimize)
        HopcroftLexer = LexicalAnalyzer.parse("TestDFAMinimization.rules", "utf8", minimizer=HopcroftDFAMinimizer.minimize)
        NaiveLexer.finalize()
        HopcroftLexer.finalize()
        final_state_count_expected = 224
        self.assertEqual(NaiveLexer.get_min_dfa(), HopcroftLexer.get_min_dfa())
        self.assertEqual(len([state for state in NaiveLexer.get_min_dfa()]), final_state_count_expected)
        self.assertEqual(len([state for state in HopcroftLexer.get_min_dfa()]), final_state_count_expected)
        
if __name__ == '__main__':
    unittest.main()