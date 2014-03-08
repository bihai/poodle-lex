import sys
sys.path.append("..")
import unittest
from Generator.RegexVariableResolver import RegexVariableResolver
from Generator.RegexParser import RegexParser
from Generator.RegexExceptions import *
from Generator import LexicalAnalyzer
from Generator import Regex

class TestRegexResolver(unittest.TestCase):
    def test_simple_case(self):
        defines = {
            'a': LexicalAnalyzer.Pattern("[abc]+"),
            'b': LexicalAnalyzer.Pattern("[xyz]*{a}d")
        }
        regex = RegexParser("Hello{b}Ok").parse()
        resolver = RegexVariableResolver(defines)
        regex.accept(resolver)
        resolved = resolver.get()
        expected = Regex.Concatenation([
            Regex.Literal([(ord('H'), ord('H'))]),
            Regex.Literal([(ord('e'), ord('e'))]),
            Regex.Literal([(ord('l'), ord('l'))]),
            Regex.Literal([(ord('l'), ord('l'))]),
            Regex.Literal([(ord('o'), ord('o'))]),
            Regex.Concatenation([
                Regex.Repetition(
                    Regex.Literal([((ord('x'), ord('z')))]), 0, Regex.Repetition.Infinity),
                Regex.Repetition(
                    Regex.Literal([((ord('a'), ord('c')))]), 1, Regex.Repetition.Infinity),
                Regex.Literal([(ord('d'), ord('d'))])]),
            Regex.Literal([(ord('O'), ord('O'))]),
            Regex.Literal([(ord('k'), ord('k'))])])
        self.assertEqual(repr(resolved), repr(expected))
    
    def test_circular(self):
        defines = {
            'Cat': LexicalAnalyzer.Pattern("Hello{Dog}Goodbye"),
            'Dog': LexicalAnalyzer.Pattern("Start{Cow}Stop"),
            'Cow': LexicalAnalyzer.Pattern("Up{Cat}Down")
        }
        unresolved = Regex.Variable("Cat")
        resolver = RegexVariableResolver(defines)
        self.assertRaises(RegexParserCircularReference, lambda: unresolved.accept(resolver))
        
    
    def test_undefined(self):
        unresolved = RegexParser("Hello{Dog}Goodbye").parse()
        resolver = RegexVariableResolver({})
        self.assertRaises(RegexParserUndefinedVariable, lambda: unresolved.accept(resolver))
    
if __name__ == '__main__':
    unittest.main()