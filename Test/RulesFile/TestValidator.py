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
from Generator.RulesFile import Validator

class TestValidator(unittest.TestCase):
    def test_invalid_command_combinations(self):
        """
        Test that invalid combinations of rule commands are caught
        """
        anonymous_nonskip = Section('::main::', None, rule = [
            Rule(None, 
                pattern = "AnonymousRuleWithNonSkipCommands",
                rule_action = ['capture'])])
        self.assertRaises(RulesFileException, lambda: anonymous_nonskip.accept(Traverser(Validator())))
        
        skip_capture = Section('::main::', None, rule = [
            Rule('SkipCapture',
                pattern = 'SkipCapture',
                rule_action = ['skip', 'capture'])])
        self.assertRaises(RulesFileException, lambda: skip_capture.accept(Traverser(Validator())))

        reserve_skip = Section('::main::', None, rule = [
            Rule('ReserveSkip',
                pattern = 'ReserveSkip',
                rule_action = ['reserve', 'skip'])])
        self.assertRaises(RulesFileException, lambda: reserve_skip.accept(Traverser(Validator())))

        reserve_import = Section('::main::', None, rule = [
            Rule('ReserveImport',
                pattern = 'ReserveImport',
                rule_action = ['reserve', 'import'])])
        self.assertRaises(RulesFileException, lambda: reserve_import.accept(Traverser(Validator())))
                
        reserve_capture = Section('::main::', None, rule = [
            Rule('ReserveCapture',
                pattern = 'ReserveCapture',
                rule_action = ['reserve', 'capture'])])
        self.assertRaises(RulesFileException, lambda: reserve_capture.accept(Traverser(Validator())))
        
    def test_section_with_no_rules(self):
        """
        Test that sections with no rules are caught
        """
        no_rules = Section('::main::', None, rule = [
            Rule('OkRule', pattern=Pattern('OkRule'))], section = [
            Section('EmptySection,', None, rule = [])])
        self.assertRaises(RulesFileException, lambda: no_rules.accept(Traverser(Validator())))
        
    def test_duplicate_names(self):
        """
        Test that duplicate rules names are caught correctly
        """
        duplicate_rule = Section('::main::', None, rule = [
            Rule('DuplicateRule', pattern=Pattern('DuplicateRule1')),
            Rule('DuplicateRule', pattern=Pattern('DuplicateRule2'))])
        self.assertRaises(RulesFileException, lambda: duplicate_rule.accept(Traverser(Validator())))

        duplicate_rule_other_section = Section('::main::', None, rule = [
            Rule('DuplicateRule', pattern=Pattern('DuplicateRule1'))], section = [
            Section('OtherSection', None, rule = [
                Rule('DuplicateRule', pattern=Pattern('DuplicateRule2'))])])
        self.assertRaises(RulesFileException, lambda: duplicate_rule_other_section.accept(Traverser(Validator())))
        
        # Only test this in same scope, since defines allowed to be duplicate in other scopes, unlike rule names.
        duplicate_define = Section('::main::', None, define = [
            Define('DuplicateDefine', pattern=Pattern('DuplicateDefine')),
            Define('DuplicateDefine', pattern=Pattern('DuplicateDefine'))], rule = [
            Rule('ReferencingRule', pattern=Pattern('{DuplicateDefine}'))])
            
        # duplicate_rule_not_reserved = Section('::main::', None, rule = [
            # Rule('DuplicateRule', pattern = 'DuplicateRule1'), 
            # Rule('DuplicateRule', 
                # pattern = 'DuplicateRule2',
                # rule_action=['import'])])
        # self.assertRaises(RulesFileException, lambda: duplicate_rule_not_reserved.accept(Traverser(Validator())))
        
        import_ok_pattern_not_reserved = Section('::main::', None, rule = [
            Rule('DuplicateRule', 
                pattern = None,
                rule_action = ['reserve']),
            Rule('DuplicateRule',
                pattern = 'DuplicateRule',
                rule_action = ['import'])])
        # Should not raise an exception
        import_ok_pattern_not_reserved.accept(Traverser(Validator()))
        
        import_ok_pattern_reserved = Section('::main::', None, rule = [
            Rule('DuplicateRule', 
                pattern = 'DuplicateRulePattern',
                rule_action = ['reserve']),
            Rule('DuplicateRule',
                pattern = None,
                rule_action = ['import'])])
        # Should not raise an exception
        import_ok_pattern_reserved.accept(Traverser(Validator()))
        
if __name__ == '__main__':
    unittest.main()