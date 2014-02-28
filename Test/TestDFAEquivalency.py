import sys
sys.path.append("..")
import unittest
from Generator import Automata
from Generator.CoverageSet import CoverageSet

def get_simple_dfa():
    # Identical DFAs
    dfa = Automata.DeterministicFiniteAutomata()
    dfa_s = [Automata.DeterministicState() for i in xrange(4)]
    dfa_s[0].edges[dfa_s[1]] = CoverageSet([(0, 1), (2, 3)])
    dfa_s[1].edges[dfa_s[2]] = CoverageSet([(0, 1), (2, 3)])
    dfa_s[1].edges[dfa_s[3]] = CoverageSet([(5, 7)])
    dfa_s[2].is_final = True
    dfa_s[2].final_ids = set(['Hello', 'Goodbye'])
    dfa_s[3].is_final = True
    dfa_s[3].final_ids = set(['Goodbye'])
    dfa.start_state = dfa_s[0]
    return (dfa, dfa_s)
    
class TestDFAEquivalency(unittest.TestCase):
    def test_identical_dfas(self):
        dfa1, dfa1_s = get_simple_dfa()
        dfa2, dfa2_s = get_simple_dfa()
        self.assertEqual(dfa1, dfa2)
        self.assertEqual(dfa2, dfa1)
        
        # Swap identities - should still be equal
        (dfa1_s[1].edges[dfa1_s[2]], dfa1_s[1].edges[dfa1_s[3]]) = (dfa1_s[1].edges[dfa1_s[3]], dfa1_s[1].edges[dfa1_s[2]])
        (dfa1_s[2].final_ids, dfa1_s[3].final_ids) = (dfa1_s[3].final_ids, dfa1_s[2].final_ids)
        self.assertEqual(dfa2, dfa1)
        self.assertEqual(dfa1, dfa2)
        
    def test_nonidentical_dfas_finalids(self):
        dfa1, dfa1_s = get_simple_dfa()
        dfa2, dfa2_s = get_simple_dfa()
        dfa1_s[3].final_ids = set()
        self.assertNotEqual(dfa2, dfa1)
        self.assertNotEqual(dfa1, dfa2)
        
    def test_nonidentical_dfas_missingedge(self):
        dfa1, dfa1_s = get_simple_dfa()
        dfa2, dfa2_s = get_simple_dfa()
        del dfa2_s[1].edges[dfa2_s[2]]
        self.assertNotEqual(dfa1, dfa2)
        self.assertNotEqual(dfa2, dfa1)
        
    def test_nonidentical_dfas_swappededges(self):
        dfa1, dfa1_s = get_simple_dfa()
        dfa2, dfa2_s = get_simple_dfa()
        (dfa1_s[1].edges[dfa1_s[2]], dfa1_s[1].edges[dfa1_s[3]]) = (dfa1_s[1].edges[dfa1_s[3]], dfa1_s[1].edges[dfa1_s[2]])
        self.assertNotEqual(dfa1, dfa2)
        self.assertNotEqual(dfa2, dfa1)
                
if __name__ == '__main__':
    unittest.main()