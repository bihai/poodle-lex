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
        
    def test_variable(self):
        parsed = RegexParser(ur"[[:alpha:]]{1,32}{Hello}{2,34}").parse()
        expected = Regex.Concatenation([
            Regex.Repetition(
                Regex.Literal([(ord(u"a"), ord(u"z")), (ord(u"A"), ord(u"Z"))]), 1, 32),
            Regex.Repetition(
                Regex.Variable("Hello"), 2, 34)])
        self.assertEqual(repr(parsed), repr(expected))
        
    def test_codepoint(self):
        parsed = RegexParser(u"\\xa3").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0xa3, 0xa3)])))
        parsed = RegexParser(u"\\u123e").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0x123e, 0x123e)])))
        parsed = RegexParser(u"\\U10ffff").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0x10ffff, 0x10ffff)])))
        
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
        self.assertRaises(RegexParserExceptionInternal, RegexParser(u"Hello{20,1}").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{a,1}").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello{1,a}").parse)
        
        # Variables
        self.assertRaises(RegexParserExpected, RegexParser(u"{Hello").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"{Hello2}").parse)
        
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
        
        # Arbitrary codepoints
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\x").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\xs").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\xa").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\xas").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\u").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\us").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\u0").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\u1s").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\u1a").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\u1at").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\u1a2").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\u1a2u").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\Uh").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8i").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8f").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8fj").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8f7").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8f7k").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8f7E").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8f7El").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8f7E6").parse)
        self.assertRaises(RegexParserExpected, RegexParser(u"Hello\\U8f7E6m").parse)
        self.assertRaises(RegexParserUnicodeCodepointOutOfRange, RegexParser(u"Hello\\U8f7E6d").parse)
                
if __name__ == '__main__':
    unittest.main()