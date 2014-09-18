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
        
    def test_unicode(self):
        parsed = Regex.Parser(u"\p{Name=Nonsense}").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([])))
        parsed = Regex.Parser(u"\p{Name=MONGOLIAN-todo Soft_HYPHEN}").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0x1806, 0x1806)])))
        parsed = Regex.Parser(u"\p{Name: MONGOLIAN-todo Soft_HYPHEN}").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0x1806, 0x1806)])))
        parsed = Regex.Parser(u"\p{na=MONGOLIAN-todo Soft_HYPHEN}").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0x1806, 0x1806)])))
        parsed = Regex.Parser(u"\p{na:MONGOLIAN-todo Soft_HYPHEN}").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(0x1806, 0x1806)])))
        parsed = Regex.Parser(u"\p{General Category=Pd}").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([
            (0x2d, 0x2d), (0x58A, 0x58a), (0x5be, 0x5be), (0x1400, 0x1400), (0x1806, 0x1806),
            (0x2010, 0x2015), (0x2E17, 0x2E17), (0x2E1A, 0x2E1A), (0x2E3A, 0x2E3B), (0x2E40, 0x2E40),
            (0x301C, 0x301C), (0x3030, 0x3030), (0x30A0, 0x30A0), (0xFE31, 0xFE32), (0xFe58, 0xFE58), 
            (0xFE63, 0xFE63), (0xFF0D, 0xFF0D)
        ])))
        
    def test_grouping_and_subexpressions(self):
        parsed = Regex.Parser("[a-z--h]").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(97, 103), (105, 122)])))
        parsed = Regex.Parser("[[a-z]--h]").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(97, 103), (105, 122)])))
        parsed = Regex.Parser("[[a-z]--[h]]").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(97, 103), (105, 122)])))
        parsed = Regex.Parser("[[a-z]--g[h]]").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(97, 102), (105, 122)])))
        parsed = Regex.Parser("[[a-z]--[gh--g]]").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(97, 103), (105, 122)])))
        parsed = Regex.Parser("[a-h~~h-z]").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(97, 103), (105, 122)])))
        parsed = Regex.Parser("[a-h||h-z]").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(97, 122)])))
        parsed = Regex.Parser("[a-h&&h-z]").parse()
        self.assertEqual(repr(parsed), repr(Regex.Literal([(104, 104)])))
        
        
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
        self.assertRaises(RegexParserExpected, Regex.Parser(u")Hello").parse)
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
        
        # Unicode
        self.assertRaises(RegexParserExpected, Regex.Parser(u"\p").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"\pLetter").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"\p{").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"\p{Letter").parse)
        self.assertRaises(ValueError, Regex.Parser(u"\p{Hello}").parse)
        self.assertRaises(ValueError, Regex.Parser(u"\p{Nothing=None}").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"\p{Name=").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"\p{Name=}").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"\p{Name:").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"\p{Name:}").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[\p]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[\pLetter]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[\p{]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[\p{Letter]").parse)
        self.assertRaises(ValueError, Regex.Parser(u"[\p{Hello}]").parse)
        self.assertRaises(ValueError, Regex.Parser(u"[\p{Nothing=None}]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[\p{Name=]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[\p{Name=}]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[\p{Name:]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[\p{Name:}]").parse)
        
        # Set operations and groups
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[[hello]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello--").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello~~").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello&&").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello||").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello--goodbye").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello~~goodbye").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello&&goodbye").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello||goodbye").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello--]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello~~]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello&&]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello||]").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"[--hello]").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"[~~hello]").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"[&&hello]").parse)
        self.assertRaises(RegexParserInvalidCharacter, Regex.Parser(u"[||hello]").parse)
        self.assertRaises(RegexParserExpected, Regex.Parser(u"[hello]]").parse)
        

if __name__ == '__main__':
    unittest.main()