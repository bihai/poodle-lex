import sys
sys.path.append("..")
import unittest
from Generator.RegexParser import RegexParser
from Generator.RegexExceptions import *
from Generator import Regex

class TestRegexParser(unittest.TestCase):
    def test_float_pattern(self):
        expected = Regex.Alternation([
            Regex.Concatenation([
                Regex.Repetition(
                    Regex.Literal([(ord(u"0"), ord(u"9"))]), 1, -1),
                Regex.Literal([(ord(u"."), ord(u"."))]),
                Regex.Repetition(
                    Regex.Literal([(ord(u"0"), ord(u"9"))]), 0, -1)]),
            Regex.Concatenation([
                Regex.Repetition(
                    Regex.Literal([(ord(u"0"), ord(u"9"))]), 0, -1),
                Regex.Literal([(ord(u"."), ord(u"."))]),
                Regex.Repetition(
                    Regex.Literal([(ord(u"0"), ord(u"9"))]), 1, -1)])])
        parsed = RegexParser(ur"[[:digit:]]+\.[0-9]*|[0-9]*\.[0-9]+").parse()
        self.assertEqual(repr(parsed), repr(expected))
    
    def test_syntax_errors(self):
        # Mismatched parenthesis
        self.assertRaises(RegexParserExpected, RegexParser(u"(Hello").parse)
        self.assertRaises(RegexParserExpected, RegexParser(ur"(Hello\)").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"(Hello))").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"(Hel(lo)))").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello(").parse)        
        
        # Out-of-place special characters
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\").parse)
        self.assertRaises(RegexParserInvalidCharacter, RegexParser(u"+Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, RegexParser(u"?Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, RegexParser(u"|Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, RegexParser(u")Hello").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hel)lo").parse)
        self.assertRaises(RegexParserInvalidCharacter, RegexParser(u":Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, RegexParser(u"*Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, RegexParser(u"^Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, RegexParser(u"He^llo").parse)

        # Repetitions
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{1").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{1,").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{1,").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{1,2").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{20,1}").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{a,1}").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{1,a}").parse)
        
        # Character classes
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[a").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[a-").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[a-z").parse)
        self.assertRaises(RegexParserInvalidCharacterRange, RegexParser(u"Hello[z-a]").parse)
        self.assertRaises(RegexParserInvalidCharacterRange, RegexParser(u"Hello[\d-9]").parse)
        
        # POSIX named character classes
        self.assertRaises(RegexParserInvalidCharacter, RegexParser(u"Hello[:alnum:]").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[[").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[[:").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[[:alnum").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[[:alnum:").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[[:alnum:]").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[[]").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[[:]").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello[[:alnum]").parse)
                
if __name__ == '__main__':
    unittest.main()