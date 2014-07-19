import sys
sys.path.append("..")
import unittest
from Generator import Regex
from Generator.Regex import RegexParserExpected, RegexParserInvalidCharacter, RegexParserInvalidCharacterRange, RegexParserExceptionInternal, RegexParserUnicodeCodepointOutOfRange

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
        parsed = Regex.Parser(ur"[[:digit:]]+\.[0-9]*|[0-9]*\.[0-9]+").parse()
        self.assertEqual(repr(parsed), repr(expected))
        
    def test_variable(self):
        parsed = Regex.Parser(ur"[[:alpha:]]{1,32}{Hello}{2,34}").parse()
        expected = Regex.Concatenation([
            Regex.Repetition(
                Regex.Literal([(ord(u"a"), ord(u"z")), (ord(u"A"), ord(u"Z"))]), 1, 32),
            Regex.Repetition(
                Regex.Variable("Hello"), 2, 34)])
        self.assertEqual(repr(parsed), repr(expected))
        
    def test_codepoint(self):
        parsed = Regex.Parser(u"\\xa3").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0xa3, 0xa3)])))
        parsed = Regex.Parser(u"\\u123e").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0x123e, 0x123e)])))
        parsed = Regex.Parser(u"\\U10ffff").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0x10ffff, 0x10ffff)])))
        
    def test_syntax_errors(self):
        # Mismatched parenthesis
        self.assertRaises(RegexParserExpected, Regex.Parser(u"(Hello").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(ur"(Hello\)").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"(Hello))").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"(Hel(lo)))").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello(").parse)        
        
        # Out-of-place special characters
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"+Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"?Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"|Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u")Hello").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hel)lo").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u":Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"*Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"^Hello").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"He^llo").parse)

        # Repetitions
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello{").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello{1").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello{1,").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello{1,").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello{1,2").parse)
        self.assertRaises(RegexParserExceptionInternal, Regex.Parser(u"Hello{20,1}").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello{a,1}").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello{1,a}").parse)
        
        # Variables
        self.assertRaises(RegexParserExpected, Regex.Parser(u"{Hello").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"{Hello2}").parse)
        
        # Character classes
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[a").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[a-").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[a-z").parse)
        self.assertRaises(RegexParserInvalidCharacterRange, Regex.Parser(u"Hello[z-a]").parse)
        self.assertRaises(RegexParserInvalidCharacterRange, Regex.Parser(u"Hello[\d-9]").parse)
        
        # POSIX named character classes
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"Hello[:alnum:]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[[").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[[:").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[[:alnum").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[[:alnum:").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[[:alnum:]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[[]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[[:]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello[[:alnum]").parse)
        
        # Arbitrary codepoints
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\x").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\xs").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\xa").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\xas").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\u").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\us").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\u0").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\u1s").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\u1a").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\u1at").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\u1a2").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\u1a2u").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\Uh").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8i").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8f").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8fj").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8f7").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8f7k").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8f7E").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8f7El").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8f7E6").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"Hello\\U8f7E6m").parse)
        self.assertRaises(RegexParserUnicodeCodepointOutOfRange, Regex.Parser(u"Hello\\U8f7E6d").parse)
                
if __name__ == '__main__':
    unittest.main()