# coding=utf8

import sys
sys.path.append("..")
import unittest
from Generator import Automata
from Generator.CoverageSet import CoverageSet
from Generator.RulesFile import AST, NonDeterministicIR, DeterministicIR

def hash_ids(*ids):
    rules = set()
    for id in ids:
        rules.add(hash((id.lower(), frozenset(), (None, None))))
    return frozenset(rules)
   
class TestDFAEquivalency(unittest.TestCase):
    def test_lexical_analyzer(self):
        # Generate DFA through the LexicalAnalyzer class
        rules_file = AST.Section("::main::", None, rule = [
            AST.Rule("keyword", AST.Pattern(ur'k€yword', is_case_insensitive=True)),
            AST.Rule("identifier", AST.Pattern(ur'[a-zA-Z][a-zA-Z0-9€_]*', is_case_insensitive=True)),
            AST.Rule("float", AST.Pattern(ur'[0-9]+\.[0-9]*|[0-9]*\.[0-9]+')),
            AST.Rule("integer", AST.Pattern(ur'[[:digit:]]+')),
            AST.Rule("quote", AST.Pattern(ur'"([^"\\]|\\.)*"')),
            AST.Rule("newline", AST.Pattern(ur'\r\n|\r|\n')),
            AST.Rule("whitespace", AST.Pattern(ur'[\t\s]+'))])
        nfa_ir = NonDeterministicIR(rules_file)
        dfa_ir = DeterministicIR(nfa_ir)
        
        # Compare DFA to expected minimized DFA
        expected_dfa = Automata.DeterministicFinite()
        dfa_s = [Automata.DeterministicState() for i in xrange(18)]
        
        #Start state
        dfa_s[0].ids = hash_ids("float", "whitespace", "keyword", "integer", "quote", "identifier", "newline")
        
        #quote
        dfa_s[0].edges[dfa_s[2]] = CoverageSet([(34, 34)])
        dfa_s[2].is_final = False
        dfa_s[2].ids = hash_ids("quote")
        dfa_s[2].edges[dfa_s[10]] = CoverageSet([(92, 92)])
        dfa_s[2].edges[dfa_s[2]] = CoverageSet([(1, 33), (35, 91), (93, 0x10FFFF)])
        dfa_s[10].is_final = False
        dfa_s[10].ids = hash_ids("quote")
        dfa_s[10].edges[dfa_s[2]] = CoverageSet([(1, 0x10FFFF)])
        dfa_s[2].edges[dfa_s[9]] = CoverageSet([(34, 34)])
        dfa_s[9].is_final = True
        dfa_s[9].final_ids = hash_ids("quote")
        dfa_s[9].ids = hash_ids("quote")
        
        #newline
        dfa_s[0].edges[dfa_s[3]] = CoverageSet([(13, 13)])
        dfa_s[0].edges[dfa_s[1]] = CoverageSet([(10, 10)])
        dfa_s[3].is_final = True
        dfa_s[3].ids = hash_ids("newline")
        dfa_s[3].final_ids = hash_ids("newline")
        dfa_s[3].edges[dfa_s[1]] = CoverageSet([(10, 10)])
        dfa_s[1].is_final = True
        dfa_s[1].ids = hash_ids("newline")
        dfa_s[1].final_ids = hash_ids("newline")
        
        #identifier
        dfa_s[0].edges[dfa_s[5]] = CoverageSet([(65, 74), (76, 90), (97, 106), (108, 122)])
        dfa_s[5].is_final = True
        dfa_s[5].ids = hash_ids("identifier")
        dfa_s[5].final_ids = hash_ids("identifier")
        dfa_s[5].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 90), (95, 95), (97, 122), (0x20ac, 0x20ac)])
        
        #integer
        dfa_s[0].edges[dfa_s[4]] = CoverageSet([(48, 57)])
        dfa_s[4].is_final = True
        dfa_s[4].ids = hash_ids("integer","float")
        dfa_s[4].final_ids = hash_ids("integer")
        dfa_s[4].edges[dfa_s[4]] = CoverageSet([(48, 57)])
        dfa_s[4].edges[dfa_s[11]] = CoverageSet([(46, 46)])
        
        #float
        dfa_s[0].edges[dfa_s[6]] = CoverageSet([(46, 46)])
        dfa_s[6].is_final = False
        dfa_s[6].ids = hash_ids("float")
        dfa_s[6].edges[dfa_s[11]] = CoverageSet([(48, 57)])
        dfa_s[11].is_final = True
        dfa_s[11].ids = hash_ids("float")
        dfa_s[11].final_ids = hash_ids("float")
        dfa_s[11].edges[dfa_s[11]] = CoverageSet([(48, 57)])
        
        #whitespace
        dfa_s[0].edges[dfa_s[7]] = CoverageSet([(9, 9), (32, 32)])
        dfa_s[7].is_final = True
        dfa_s[7].ids = hash_ids("whitespace")
        dfa_s[7].final_ids = hash_ids("whitespace")
        dfa_s[7].edges[dfa_s[7]] = CoverageSet([(9, 9), (32, 32)])
        
        #keyword
        dfa_s[0].edges[dfa_s[8]] = CoverageSet([(75, 75), (107, 107)])
        dfa_s[8].is_final = True
        dfa_s[8].ids = hash_ids("identifier", "keyword")
        dfa_s[8].final_ids = hash_ids("identifier")
        dfa_s[8].edges[dfa_s[12]] = CoverageSet([(0x20ac, 0x20ac)])
        dfa_s[8].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 90), (95, 95), (97, 122)])
        dfa_s[12].is_final = True
        dfa_s[12].ids = hash_ids("identifier", "keyword")
        dfa_s[12].final_ids = hash_ids("identifier")
        dfa_s[12].edges[dfa_s[13]] = CoverageSet([(121, 121), (89, 89)])
        dfa_s[12].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 88), (90, 90), (95, 95), (97, 120), (122, 122), (0x20ac, 0x20ac)])
        dfa_s[13].is_final = True
        dfa_s[13].ids = hash_ids("identifier", "keyword")
        dfa_s[13].final_ids = hash_ids("identifier")
        dfa_s[13].edges[dfa_s[14]] = CoverageSet([(119, 119), (87, 87)])
        dfa_s[13].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 86), (88, 90), (95, 95), (97, 118), (120, 122), (0x20ac, 0x20ac)])
        dfa_s[14].is_final = True
        dfa_s[14].ids = hash_ids("identifier", "keyword")
        dfa_s[14].final_ids = hash_ids("identifier")
        dfa_s[14].edges[dfa_s[15]] = CoverageSet([(111, 111), (79, 79)])
        dfa_s[14].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 78), (80, 90), (95, 95), (97, 110), (112, 122), (0x20ac, 0x20ac)])
        dfa_s[15].is_final = True
        dfa_s[15].ids = hash_ids("identifier", "keyword")
        dfa_s[15].final_ids = hash_ids("identifier")
        dfa_s[15].edges[dfa_s[16]] = CoverageSet([(114, 114), (82, 82)])
        dfa_s[15].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 81), (83, 90), (95, 95), (97, 113), (115, 122), (0x20ac, 0x20ac)])
        dfa_s[16].is_final = True
        dfa_s[16].ids = hash_ids("identifier", "keyword")
        dfa_s[16].final_ids = hash_ids("identifier")
        dfa_s[16].edges[dfa_s[17]] = CoverageSet([(100, 100), (68, 68)])
        dfa_s[16].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 67), (69, 90), (95, 95), (97, 99), (101, 122), (0x20ac, 0x20ac)])
        dfa_s[17].is_final = True
        dfa_s[17].ids = hash_ids("identifier", "keyword")
        dfa_s[17].final_ids = hash_ids("identifier","keyword")
        dfa_s[17].edges[dfa_s[5]] = CoverageSet([(48, 57), (65, 90), (95, 95), (97, 122), (0x20ac, 0x20ac)])
        
        expected_dfa.start_state = dfa_s[0]
        self.assertEqual(dfa_ir.sections.values()[0].dfa, expected_dfa)
    
if __name__ == '__main__':
    unittest.main()
