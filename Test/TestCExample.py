import sys
sys.path.append("..")
import os
import os.path
import shutil
import unittest
import tempfile
import subprocess
import difflib

from Generator.LexicalAnalyzerParser import LexicalAnalyzerParserException
from Generator.LexicalAnalyzer import LexicalAnalyzer
from Generator.RegexParser import RegexParser
from Generator.RegexExceptions import *
from Generator import HopcroftDFAMinimizer
from Generator import LanguagePlugins

base_directory = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

class TestCExampleFreeBasic(unittest.TestCase):
    def run_poodle_lex(self, language):
        output_dir = tempfile.mkdtemp()
        rules_file = os.path.join(base_directory, "Example", "CLexer", "CLexer.rules")
        lexer = LexicalAnalyzer.parse(rules_file, "utf-8", HopcroftDFAMinimizer.minimize)
        language_plugins, default_language = LanguagePlugins.load(base_directory, "Plugins/Plugins.json", 'utf-8')
        language_plugins[language].load()
        language_plugin = language_plugins[language]
        plugin_options = LanguagePlugins.PluginOptions()
        emitter = language_plugin.create(lexer, output_dir, plugin_options)
        for directory_name in emitter.get_output_directories():
            real_directory_name = os.path.join(output_dir, directory_name)
            if not os.path.exists(real_directory_name):
                os.mkdir(real_directory_name)
        for file in emitter.get_files_to_copy():
            shutil.copy(os.path.join(language_plugin.plugin_files_directory, file), os.path.join(output_dir, file))
        emitter.emit()
        return output_dir

    def run_demo(self, output_dir, demo_base_name):
        working_dir = os.path.join(output_dir, demo_base_name)
        resource_directory = os.path.join(base_directory, "Test", "TestCExample")
        demo_input = os.path.join(resource_directory, "sqlite3.c")
        demo_output = os.path.join(working_dir, "output.txt")
        expected_output = os.path.join(resource_directory, "expected_output.txt")
        with open(os.devnull, 'w') as f:
            if os.name == 'posix':
                demo_exe = os.path.join(working_dir, demo_base_name)
                subprocess.call('./make_demo.sh', cwd=working_dir, shell=True, stdout=f)
            else:
                demo_exe = os.path.join(working_dir, demo_base_name + ".exe")
                subprocess.call('make_demo.bat', cwd=working_dir, shell=True, stdout=f)
        with open(demo_output, 'w') as f:
            subprocess.call([demo_exe, demo_input], cwd=working_dir, stdout=f)
        
        # Compare output and expected
        matching = True
        with open(demo_output, 'r') as f1:
            with open(expected_output, 'r') as f2:
                while True:
                    actual = f1.read(4096)
                    expected = f2.read(4096)
                    if actual != expected:
                        matching = False
                    if actual == '':
                        break
        self.assertTrue(matching)
    
    def test_cexample_freebasic(self):
        output_dir = self.run_poodle_lex("freebasic")
        self.run_demo(output_dir, "Demo")
        
    def test_cexample_cpp(self):
        output_dir = self.run_poodle_lex("cpp")
        self.run_demo(output_dir, "demo")
            
if __name__ == '__main__':
    unittest.main()