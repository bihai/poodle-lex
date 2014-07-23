# coding=utf8

import os.path
import sys
import xml.etree.ElementTree as ET
import unittest
from StringIO import StringIO
from TestASTComparer import TestASTComparer
sys.path.append(os.path.join("..", ".."))
from Generator.RulesFile import Parser
from Generator.RulesFile.AST import *

   
class TestParser(unittest.TestCase):
    def test_bad_rules(self):
        tree = ET.parse('TestParserBad.xml')
        root = tree.getroot()
        for child in root:
            test_name = child.attrib['name']
            test_content = child.text
            stream = StringIO(test_content)
            if 'type' not in child.attrib or child.attrib['type'] != 'pass':
                self.assertRaises(RulesFileException, lambda: Parser.parse_stream(stream))

    def test_rules_file(self):
        actual = Parser.parse('TestParserGood.rules')
        expected = Section('::main::', rule = [
            Rule(None, 
                pattern=Pattern('AnonymousSkippedRule'), 
                rule_action=['skip']),
            Rule(None, 
                pattern=Pattern('AnonymousSkippedRuleEnteringSection'),
                rule_action=['skip'],
                section_action=('enter', Section(None, rule = [
                    Rule(None,
                        pattern=Pattern('AnonymousRuleExitingSection'),
                        rule_action=['skip'],
                        section_action=('exit', None)),
                    Rule('RuleReservationWithPattern',
                        pattern=None,
                        rule_action=['import','skip'])]))),
            Rule('RuleEnteringExistingSection', 
                pattern=Pattern('AnnYeong'),
                section_action=('enter', SectionReference('StandaloneSection'))),
            Rule('RuleEnteringNewSection', 
                pattern=Pattern('Hallo'),
                section_action=('enter', Section('RuleEnteringNewSection', rule = [
                    Rule('RuleInSection', pattern=Pattern('Hi')),
                    Rule('RuleInSectionThatExits',
                        pattern=Pattern("Kon'nichiwa"),
                        section_action=('exit', None))]))),
            Rule('RuleEnteringNewSectionThatInherits',
                pattern=Pattern('Salam Alaykum'),
                section_action=('enter', Section('RuleEnteringNewSectionThatInherits', rule = [
                    Rule('RuleInSectionWithCommand',
                        pattern=Pattern('{DefineInSection}'),
                        rule_action=['skip'],
                        section_action=('exit', None))], define = [
                    Define('DefineInSection', Pattern('Shalom'))],
                    inherits=True))),
            Rule('RuleReservation', 
                pattern=None,
                rule_action=['reserve']),
            Rule('RuleReservationWithPattern', 
                pattern=None,
                rule_action = ['import']),
            Rule('RuleReservationWithPattern', 
                pattern=Pattern("NiHao"),
                rule_action=['reserve']),
            Rule('RuleWithCommand',
                pattern=Pattern('Bonjour'),
                rule_action=['capture']),
            Rule('RuleWithComment', pattern=Pattern('Ciao')),
            Rule('RuleWithConcatenation', pattern=Pattern('ComoEstasMuyBien')),
            Rule('RuleWithEscapeQuotes', pattern=Pattern('"Hola"')),
            Rule('RuleCaseInsensitive', pattern=Pattern('Greetings', True)),
            Rule('RuleReservation',
                pattern=Pattern('RuleWithMultipleCommands'),
                rule_action=['import', 'capture']),
            Rule('RuleWithMultipleLines', pattern=Pattern('HowDoYouDo?')),
            Rule('RuleWithMultipleLinesAndComment', pattern=Pattern('HowIsMother?')),
            Rule('RuleWithPattern', pattern=Pattern('GutenTag'))], define = [
            Define('Definition', pattern=Pattern('Hello'))], section = [
            Section('StandaloneSection', rule = [
                Rule('RuleInSectionWithNestedSection', 
                    pattern=Pattern('Aloha'),
                    section_action=('enter', Section('RuleInSectionWithNestedSection', rule = [
                        Rule('RuleInsideNestedSection',
                            pattern=Pattern('E Kaaro'),
                            section_action=('exit', None))]))),
                Rule('RuleInSectionWithNestedSectionThatInherits',
                    pattern=Pattern('Hej'),
                    section_action=('enter', Section('RuleInSectionWithNestedSectionThatInherits', rule = [
                        Rule('RuleInsideNestedSectionTHatInherits',
                            pattern=Pattern('E Kaasan'),
                            section_action=('exit', None))],
                        inherits=True)))], section = [
                Section('NestedStandaloneSection', rule = [
                    Rule('RuleInsideNestedStandaloneSection',
                        pattern=Pattern('E Kale'),
                        section_action=('exit', None))])])])
        TestASTComparer.compare(expected, actual)
        self.assertEqual(expected, actual)
        
if __name__ == '__main__':
    unittest.main()
