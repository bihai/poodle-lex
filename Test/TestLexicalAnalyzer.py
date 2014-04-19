# coding=utf8

import sys
sys.path.append("..")
import unittest
from Generator import Automata
from Generator.CoverageSet import CoverageSet
from Generator.LexicalAnalyzer import LexicalAnalyzer, Pattern

   
class TestDFAEquivalency(unittest.TestCase):
    def test_lexical_analyzer(self):
        # Generate DFA through the LexicalAnalyzer class
        lexical_analyzer = LexicalAnalyzer()
        lexical_analyzer.add_rule("Keyword", Pattern(ur'k€yword', True))
        lexical_analyzer.add_rule("Identifier", Pattern(ur'[a-zA-Z][a-zA-Z0-9€_]*', True))
        lexical_analyzer.add_rule("Float", Pattern(ur'[0-9]+\.[0-9]*|[0-9]*\.[0-9]+'))
        lexical_analyzer.add_rule("Integer", Pattern(ur'[[:digit:]]+'))
        lexical_analyzer.add_rule("Quote", Pattern(ur'"([^"\\]|\\.)*"'))
        lexical_analyzer.add_rule("Newline", Pattern(ur'\r\n|\r|\n'))
        lexical_analyzer.add_rule("Whitespace", Pattern(ur'[\t\s]+'))
        lexical_analyzer.finalize()
        min_dfa = lexical_analyzer.get_min_dfa()
        with open('got_min_dfa.dot', 'w') as f:
            f.write(repr(min_dfa))
        
        # Compare DFA to expected minimized DFA
        expected_dfa = Automata.DeterministicFiniteAutomata()
        dfa_s = [Automata.DeterministicState() for i in xrange(18)]
        
        #Start state
        dfa_s[0].ids = frozenset(("Float", "Whitespace", "Keyword", "Integer", "Quote", "Identifier", "Newline"))
        
        #Quote
        dfa_s[0].edges[dfa_s[2]] = CoverageSet([(34, 34)])
        dfa_s[2].is_final = False
        dfa_s[2].ids = frozenset(("Quote",))
        dfa_s[2].edges[dfa_s[10]] = CoverageSet([(92, 92)])
        dfa_s[2].edges[dfa_s[2]] = CoverageSet([(1, 33), (35, 91), (93, 0x10FFFF)])
        dfa_s[10].is_final = False
        dfa_s[10].ids = frozenset(("Quote",))
        dfa_s[10].edges[dfa_s[2]] = CoverageSet([(1, 0x10FFFF)])
        dfa_s[2].edges[dfa_s[9]] = CoverageSet([(34, 34)])
        dfa_s[9].is_final = True
        dfa_s[9].final_ids = frozenset(("Quote",))
        dfa_s[9].ids = frozenset(("Quote",))
        
        #Newline
        dfa_s[0].edges[dfa_s[3]] = CoverageSet([(13, 13)])
        dfa_s[0].edges[dfa_s[1]] = CoverageSet([(10, 10)])
        dfa_s[3].is_final = True
        dfa_s[3].ids = frozenset(("Newline",))
        dfa_s[3].final_ids = frozenset(("Newline",))
        dfa_s[3].edges[dfa_s[1]] = CoverageSet([(10, 10)])
        dfa_s[1].is_final = True
        dfa_s[1].ids = frozenset(("Newline",))
        dfa_s[1].final_ids = frozenset(("Newline",))
        
        #Identifier
        dfa_s[0].edges[dfa_s[5]] = CoverageSet([(65, 74), (76, 90), (97, 106), (108, 122)])
        dfa_s[5].is_final = True
        dfa_s[5].ids = frozenset(("Identifier",))
        dfa_s[5].final_ids = frozenset(("Identifier",))
        dfa_s[5].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 90), (95, 95), (97, 122), (0x20ac, 0x20ac)])
        
        #Integer
        dfa_s[0].edges[dfa_s[4]] = CoverageSet([(48, 57)])
        dfa_s[4].is_final = True
        dfa_s[4].ids = frozenset(("Integer","Float"))
        dfa_s[4].final_ids = frozenset(("Integer",))
        dfa_s[4].edges[dfa_s[4]] = CoverageSet([(48, 57)])
        dfa_s[4].edges[dfa_s[11]] = CoverageSet([(46, 46)])
        
        #Float
        dfa_s[0].edges[dfa_s[6]] = CoverageSet([(46, 46)])
        dfa_s[6].is_final = False
        dfa_s[6].ids = frozenset(("Float",))
        dfa_s[6].edges[dfa_s[11]] = CoverageSet([(48, 57)])
        dfa_s[11].is_final = True
        dfa_s[11].ids = frozenset(("Float",))
        dfa_s[11].final_ids = frozenset(("Float",))
        dfa_s[11].edges[dfa_s[11]] = CoverageSet([(48, 57)])
        
        #Whitespace
        dfa_s[0].edges[dfa_s[7]] = CoverageSet([(9, 9), (32, 32)])
        dfa_s[7].is_final = True
        dfa_s[7].ids = frozenset(("Whitespace",))
        dfa_s[7].final_ids = frozenset(("Whitespace",))
        dfa_s[7].edges[dfa_s[7]] = CoverageSet([(9, 9), (32, 32)])
        
        #Keyword
        dfa_s[0].edges[dfa_s[8]] = CoverageSet([(75, 75), (107, 107)])
        dfa_s[8].is_final = True
        dfa_s[8].ids = frozenset(("Identifier", "Keyword"))
        dfa_s[8].final_ids = frozenset(("Identifier",))
        dfa_s[8].edges[dfa_s[12]] = CoverageSet([(0x20ac, 0x20ac)])
        dfa_s[8].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 90), (95, 95), (97, 122)])
        dfa_s[12].is_final = True
        dfa_s[12].ids = frozenset(("Identifier", "Keyword"))
        dfa_s[12].final_ids = frozenset(("Identifier",))
        dfa_s[12].edges[dfa_s[13]] = CoverageSet([(121, 121), (89, 89)])
        dfa_s[12].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 88), (90, 90), (95, 95), (97, 120), (122, 122), (0x20ac, 0x20ac)])
        dfa_s[13].is_final = True
        dfa_s[13].ids = frozenset(("Identifier", "Keyword"))
        dfa_s[13].final_ids = frozenset(("Identifier",))
        dfa_s[13].edges[dfa_s[14]] = CoverageSet([(119, 119), (87, 87)])
        dfa_s[13].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 86), (88, 90), (95, 95), (97, 118), (120, 122), (0x20ac, 0x20ac)])
        dfa_s[14].is_final = True
        dfa_s[14].ids = frozenset(("Identifier", "Keyword"))
        dfa_s[14].final_ids = frozenset(("Identifier",))
        dfa_s[14].edges[dfa_s[15]] = CoverageSet([(111, 111), (79, 79)])
        dfa_s[14].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 78), (80, 90), (95, 95), (97, 110), (112, 122), (0x20ac, 0x20ac)])
        dfa_s[15].is_final = True
        dfa_s[15].ids = frozenset(("Identifier", "Keyword"))
        dfa_s[15].final_ids = frozenset(("Identifier",))
        dfa_s[15].edges[dfa_s[16]] = CoverageSet([(114, 114), (82, 82)])
        dfa_s[15].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 81), (83, 90), (95, 95), (97, 113), (115, 122), (0x20ac, 0x20ac)])
        dfa_s[16].is_final = True
        dfa_s[16].ids = frozenset(("Identifier", "Keyword"))
        dfa_s[16].final_ids = frozenset(("Identifier",))
        dfa_s[16].edges[dfa_s[17]] = CoverageSet([(100, 100), (68, 68)])
        dfa_s[16].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 67), (69, 90), (95, 95), (97, 99), (101, 122), (0x20ac, 0x20ac)])
        dfa_s[17].is_final = True
        dfa_s[17].ids = frozenset(("Identifier", "Keyword"))
        dfa_s[17].final_ids = frozenset(("Identifier","Keyword"))
        dfa_s[17].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 90), (95, 95), (97, 122), (0x20ac, 0x20ac)])
        
        expected_dfa.start_state = dfa_s[0]
        with open('expected_min_dfa.dot', 'w') as f:
            f.write(repr(expected_dfa))

        
        self.assertEqual(min_dfa, expected_dfa)
    
if __name__ == '__main__':
    unittest.main()
