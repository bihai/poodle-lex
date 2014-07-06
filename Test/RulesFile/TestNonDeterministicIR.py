# Copyright (C) 2014 Parker Michaels
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import unittest
import sys
import os.path
sys.path.append(os.path.join("..", ".."))
from Generator.RulesFile.Lexer import RulesFileException
from Generator.RulesFile.AST import *
from Generator.RulesFile.Visitor import Traverser
from Generator.RulesFile import NonDeterministicIR

class TestNonDeterministicIR(unittest.TestCase):
    """
    Test some import_ok error and non-error cases. The presence of epsilong edges make
    NFAs themselves very difficult to compare to equivalence without converting to
    DFAs, so these tests check more cases about resolving names and storing 
    metadata
    """
    def test_anonymous_rules_ok(self):
        """
        Test that
        """
        multiple_anonymous_ok = Section('::main::', None, rule = [
            Rule(None, 
                pattern = Pattern("AnonymousRuleWithNonSkipCommands"),
                rule_action = ['capture']),
            Rule(None, 
                pattern = Pattern("AnotherAnonymousRule"),
                rule_action = ['skip']),
            Rule("ID", pattern = "NamedRule")])
            
    def test_defines(self):
        define_ok = Section('::main::', None, rule = [
            Rule('FromMain', pattern=Pattern('Main{mainId}{id}{othersection.id}{othersection.deepsection.id}'))], define = [
            Define('ID', Pattern('define1')),
            Define('MainID', Pattern('define2'))], section = [
            Section('OtherSection', None, rule = [
                Rule('FromOtherSection', pattern=Pattern('Other{mainId}{.id}{id}{deepsection.id}{sistersection.id}'))], define = [
                Define('id', Pattern('define3'))], section = [
                Section('DeepSection', None, rule = [
                    Rule('FromDeepSection', pattern=Pattern('Deep{mainId}{.id}{.othersection.id}{id}{sistersection.id}'))], define = [
                    Define('id', Pattern('define4'))])]),
            Section('SisterSection', None, rule = [
                Rule('Placeholder', pattern=Pattern('Placeholder'))], define = [
                Define('iD', Pattern('define5')),
                Define('outOfScope', Pattern('define6'))])])
        # Make sure defines are found correctly
        self.assertEqual(define_ok.find('define', 'id')[0].pattern.regex, 'define1')
        self.assertEqual(define_ok.find('define', 'mainId')[0].pattern.regex, 'define2')
        self.assertEqual(define_ok.find('define', 'OtherSection.id')[0].pattern.regex, 'define3')
        self.assertEqual(define_ok.find('define', 'OtherSection.DeepSection.id')[0].pattern.regex, 'define4')
        self.assertEqual(define_ok.find('define', 'SisterSection.id')[0].pattern.regex, 'define5')
        
        other_section = define_ok.find('section', 'otherSection')[0]
        self.assertEqual(other_section.find('define', '.id')[0].pattern.regex, 'define1')
        self.assertEqual(other_section.find('define', 'mainId')[0].pattern.regex, 'define2')
        self.assertEqual(other_section.find('define', 'id')[0].pattern.regex, 'define3')
        self.assertEqual(other_section.find('define', 'DeepSection.id')[0].pattern.regex, 'define4')
        self.assertEqual(other_section.find('define', 'SisterSection.id')[0].pattern.regex, 'define5')
        
        deep_section = other_section.find('section', 'deepSection')[0]
        self.assertEqual(deep_section.find('define', '.id')[0].pattern.regex, 'define1')
        self.assertEqual(deep_section.find('define', 'mainId')[0].pattern.regex, 'define2')
        self.assertEqual(deep_section.find('define', '.othersection.id')[0].pattern.regex, 'define3')
        self.assertEqual(deep_section.find('define', 'id')[0].pattern.regex, 'define4')
        self.assertEqual(deep_section.find('define', 'SisterSection.id')[0].pattern.regex, 'define5')
        
        # Building IR should not break anything
        define_ok_ir = NonDeterministicIR(define_ok)
        
        # Variable not found
        define_missing = Section('::main::', None, rule = [
            Rule('MissingId', Pattern('{id}'))], define = [
            Define('AnotherID', Pattern('hi'))])
        self.assertRaises(RulesFileException, lambda: NonDeterministicIR(define_missing))
        
        # Variable defined out of scope not found
        define_out_of_scope = Section('::main::', None, rule = [
            Rule('Placeholder', Pattern('Placeholder'))], section = [
            Section('ChildSection', None, rule = [
                Rule('BadReference', Pattern('{id}'))]),
            Section('SiblingSection', None, rule = [
                Rule('Placeholder2', Pattern('Placeholder2'))], define = [
                Define('id', Pattern('shouldnotbefound'))])])
                
        child_section = define_out_of_scope.find('section', 'childsection')[0]
        self.assertNotEquals(child_section, None)
        self.assertEquals(child_section.find('define', '.siblingsection.id')[0].pattern.regex, 'shouldnotbefound')
        self.assertEquals(child_section.find('define', 'id'), None)
        self.assertRaises(RulesFileException, lambda: NonDeterministicIR(define_out_of_scope))
        
    def test_import(self):
        import_ok_rule1 = Rule('ReservedID1', pattern=None, rule_action=['import'])
        import_ok_rule2 = Rule('ReservedID2', pattern=Pattern('importprovided'), rule_action=['capture', 'import'])
        
        # import from main section
        import_ok_rule_other1 = Rule('ReservedID1', pattern=None, rule_action=['capture', 'import'])
        import_ok_rule_other2 = Rule('ReservedID2', pattern=Pattern('importprovided2'), rule_action=['import'])
        
        # import from other section
        import_ok_rule3 = Rule('OtherSection.ReservedID3', pattern=None, rule_action=['capture', 'import'])
        import_ok_rule4 = Rule('OtherSection.ReservedID4', pattern=Pattern('importprovided'), rule_action=['capture', 'import'])
        
        # import from sister section
        import_ok_rule_sister3 = Rule('OtherSection.ReservedID3', pattern=None, rule_action=['import'])
        import_ok_rule_sister4 = Rule('OtherSection.ReservedID4', pattern=Pattern('importprovided'), rule_action=['capture', 'import'])
        
        import_ok_reservation1 = Rule('ReservedID1', pattern=Pattern('Hello'), rule_action = ['reserve'])
        import_ok_reservation2 = Rule('ReservedID2', pattern=None, rule_action = ['reserve'])
        import_ok_reservation3 = Rule('ReservedID3', pattern=Pattern('Goodbye'), rule_action = ['reserve'])
        import_ok_reservation4 = Rule('ReservedID4', pattern=None, rule_action = ['reserve'])
        import_ok = Section('::main::', None, 
            rule = [import_ok_rule1, import_ok_rule2, import_ok_rule3, import_ok_rule4, import_ok_reservation1, import_ok_reservation2],
            section = [
                Section('OtherSection', None,
                    rule = [import_ok_rule_other1, import_ok_rule_other2, import_ok_reservation3, import_ok_reservation4],
                    reservation = [import_ok_reservation3, import_ok_reservation4],
                    future_import = [import_ok_rule_other1, import_ok_rule_other2]),
                Section('SisterSection', None,
                    rule = [import_ok_rule_sister3, import_ok_rule_sister4],
                    future_import = [import_ok_rule_sister3, import_ok_rule_sister4])],
            future_import = [import_ok_rule1, import_ok_rule2, import_ok_rule3, import_ok_rule4],
            reservation = [import_ok_reservation1, import_ok_reservation2])
        import_ok_ir = NonDeterministicIR(import_ok)
        
        # Check that pattern imports were filled in
        self.assertNotEqual(import_ok_rule1.pattern, None)
        self.assertNotEqual(import_ok_rule3.pattern, None)
        self.assertNotEqual(import_ok_rule_other1.pattern, None)
        self.assertNotEqual(import_ok_rule_sister3.pattern, None)
        self.assertEqual(import_ok_rule1.pattern, import_ok_reservation1.pattern)
        self.assertEqual(import_ok_rule3.pattern, import_ok_reservation3.pattern)
        self.assertEqual(import_ok_rule_other1.pattern, import_ok_reservation1.pattern)
        self.assertEqual(import_ok_rule_sister3.pattern, import_ok_reservation3.pattern)
        
        # Check that rule reservations were untouched
        self.assertEqual(import_ok_reservation2.pattern, None)
        self.assertEqual(import_ok_reservation4.pattern, None)
        
        # Import from missing reservation
        import_not_found_reservation = Rule('WrongReservation', Pattern('SomeRule'), rule_action=['reserve'])
        import_not_found_rule = Rule('ReservedId', None, rule_action=['import'])
        import_not_found = Section('::main::', None, 
            rule = [import_not_found_reservation, import_not_found_rule],
            reservation = [import_not_found_reservation],
            future_import = [import_not_found_rule])
        self.assertRaises(RulesFileException, lambda: NonDeterministicIR(import_not_found))
        
        # Import from reserved ID which is out of scope
        import_out_of_scope_rule = Rule('ReservedId', None, rule_action=['import'])
        import_out_of_scope_reservation = Rule('ReservedId', Pattern('SomePattern'), rule_action=['reserve'])
        import_out_of_scope = Section('::main::', None, 
            rule = [import_out_of_scope_rule],
            section = [
                Section('OtherSection', None, 
                    rule = [import_out_of_scope_reservation, Rule('Placeholder', Pattern('placeholder'))], 
                    reservation = [import_out_of_scope_reservation])],
            future_import = [import_out_of_scope_rule])
        self.assertRaises(RulesFileException, lambda: NonDeterministicIR(import_out_of_scope))
        
        # Import without defining pattern
        import_no_pattern_rule = Rule('ReservedId', None, rule_action=['import'])
        import_no_pattern_reservation = Rule('ReservedId', None, rule_action=['reserve'])
        import_no_pattern = Section('::main::', None, 
            rule = [import_no_pattern_rule, import_no_pattern_reservation],
            reservation = [import_no_pattern_reservation],
            future_import = [import_no_pattern_rule])
        self.assertRaises(RulesFileException, lambda: NonDeterministicIR(import_no_pattern_rule))
                
if __name__ == '__main__':
    unittest.main()