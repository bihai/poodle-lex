import sys
sys.path.append("..")
import os
import os.path
import shutil
import unittest
import tempfile
import subprocess
import difflib

from Generator import RulesFile
from Generator import LanguagePlugins

base_directory = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

class TestCExampleFreeBasic(unittest.TestCase):
    def run_poodle_lex(self, language):
        output_dir = tempfile.mkdtemp()
        rules_file_path = os.path.join(base_directory, "Example", "CLexer", "CLexer.rules")
        rules_file = RulesFile.Parser.parse(rules_file_path, "utf-8")
        rules_file.accept(RulesFile.Traverser(RulesFile.Validator()))
        nfa_ir = RulesFile.NonDeterministicIR(rules_file)
        dfa_ir = RulesFile.DeterministicIR(nfa_ir)
        plugin_file_path = os.path.join(base_directory, "Plugins/Plugins.json")
        language_plugins, default_language = LanguagePlugins.load(plugin_file_path, 'utf-8')
        language_plugins[language].load()
        language_plugin = language_plugins[language]
        representation = dfa_ir
        if language_plugin.default_form == LanguagePlugins.PluginOptions.NFA_IR:
            representation = nfa_ir
        plugin_options = LanguagePlugins.PluginOptions()
        emitter = language_plugin.create(representation, plugin_options)
        executor = LanguagePlugins.Executor(emitter, language_plugin.plugin_files_directory, output_dir)
        executor.execute()
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
                subprocess.call('sh make_demo.sh', cwd=working_dir, shell=True, stdout=f)
            else:
                demo_exe = os.path.join(working_dir, demo_base_name + ".exe")
                subprocess.call('make_demo.bat', cwd=working_dir, shell=True, stdout=f)
        with open(demo_output, 'w') as f:
            subprocess.call([demo_exe, demo_input], cwd=working_dir, stdout=f)
        
        # Compare output and expected
        matching = True
        with open(demo_output, 'rU') as f1:
            with open(expected_output, 'rU') as f2:
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
