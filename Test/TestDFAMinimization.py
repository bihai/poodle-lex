import sys
sys.path.append("..")
import unittest
from Generator import Automata
from Generator.CoverageSet import CoverageSet
from Generator.Automata import Minimizer
from Generator import RulesFile

class TestDFAMinimization(unittest.TestCase):
    def test_minimization_simple(self):
        dfa = Automata.DeterministicFinite()
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
        Minimizer.polynomial(dfa)
        
        min_dfa = Automata.DeterministicFinite()
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
        dfa = Automata.DeterministicFinite()
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
        
        Minimizer.polynomial(dfa)
        Minimizer.hopcroft(dfa_copy)
        
        min_dfa = Automata.DeterministicFinite()
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
        polynomial_rules = RulesFile.Parser.parse("TestDFAMinimization.rules", "utf8")
        polynomial_nfa_ir = RulesFile.NonDeterministicIR(polynomial_rules)
        polynomial_dfa_ir = RulesFile.DeterministicIR(polynomial_nfa_ir, minimizer=Minimizer.polynomial)
        polynomial_dfa = polynomial_dfa_ir.sections['::main::'].dfa
        
        hopcroft_rules = RulesFile.Parser.parse("TestDFAMinimization.rules", "utf8")
        hopcroft_nfa_ir = RulesFile.NonDeterministicIR(polynomial_rules)
        hopcroft_dfa_ir = RulesFile.DeterministicIR(polynomial_nfa_ir, minimizer=Minimizer.hopcroft)
        hopcroft_dfa = hopcroft_dfa_ir.sections['::main::'].dfa
        
        final_state_count_expected = 224
        self.assertEqual(polynomial_dfa, hopcroft_dfa)
        self.assertEqual(len([state for state in polynomial_dfa]), final_state_count_expected)
        self.assertEqual(len([state for state in hopcroft_dfa]), final_state_count_expected)
        
if __name__ == '__main__':
    unittest.main()