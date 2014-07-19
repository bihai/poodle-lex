import sys
sys.path.append("..")
import unittest

from Generator import RulesFile
from Generator import Regex
from Generator.Regex import RegexParserCircularReference, RegexParserUndefinedVariable

class TestRegexResolver(unittest.TestCase):
    def test_simple_case(self):
        defines = {
            'a': Regex.Parser("[abc]+").parse(),
            'b': Regex.Parser("[xyz]*{a}d").parse()
        }
        regex = Regex.Parser("Hello{b}Ok").parse()
        resolver = Regex.VariableResolver(defines)
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
            'Cat': Regex.Parser("Hello{Dog}Goodbye").parse(),
            'Dog': Regex.Parser("Start{Cow}Stop").parse(),
            'Cow': Regex.Parser("Up{Cat}Down").parse()
        }
        unresolved = Regex.Variable("Cat")
        resolver = Regex.VariableResolver(defines)
        self.assertRaises(RegexParserCircularReference, lambda: unresolved.accept(resolver))
        
    
    def test_undefined(self):
        unresolved = Regex.Parser("Hello{Dog}Goodbye").parse()
        resolver = Regex.VariableResolver({})
        self.assertRaises(RegexParserUndefinedVariable, lambda: unresolved.accept(resolver))
    
if __name__ == '__main__':
    unittest.main()