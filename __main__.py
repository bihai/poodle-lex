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

from __future__ import print_function
import os
import sys
import shutil
from Generator.Automata.Minimizer import hopcroft
from Generator.Automata.Minimizer import polynomial
from Generator import CommandArguments
from Generator import LanguagePlugins
from Generator import RulesFile
from Generator import LanguagePlugins

this_file = sys.executable
if getattr(sys, 'frozen', None) is None:
    this_file = __file__
this_folder = os.path.dirname(os.path.normcase(os.path.realpath(this_file)))

minimizers = {
    'hopcroft': ('Minimize using Hopcroft\'s partition refinement algorithm', hopcroft),
    'polynomial': ('Minimize using a polynomial algorithm comparing each state', polynomial),
    'none': ('Do not minimize', lambda: None)
}

# Handle 'list' commands
command, arguments = CommandArguments.handle()
if command == 'list-minimizers':
    left_column_size = len(max(minimizers, key=lambda i: len(i))) + 1
    print("Supported DFA minimization algorithms:", file=sys.stderr)
    for name, (description, minimizer) in minimizers.iteritems():
        print("    %s%s%s\n" % (name, ' '*(left_column_size-len(name)), description), file=sys.stderr)
    sys.exit(0)
elif command == 'list-languages':
    LanguagePlugins.describe(this_folder, "Plugins/Plugins.json", 'utf-8')
    sys.exit(0)
elif command == 'list-forms':
    print("Supported State Machine Forms (language support may vary)")
    print("    nfa     Non-deterministic finite automata")
    print("    dfa     Minimized deterministic finit automata")
    print("    default Use the default specified for the language")
    
# Check minimizer
if arguments.minimizer not in minimizers:
    print("Minimizer '%s' not recognized\n" % arguments.minimizer, file=sys.stderr)
    sys.exit(1)
minimizer_description, minimizer = minimizers[arguments.minimizer]

# Load language plug-ins file and list languages if requested
language_plugins = None
default_language = None
try:
    language_plugins, default_language = LanguagePlugins.load(this_folder, "Plugins/Plugins.json", 'utf-8')
except Exception as e: 
   print("Unable to load plug-in file: %s\n" % str(e), file=sys.stderr)
   sys.exit(1)

# Load language plug-in
language = arguments.language
if language is None:
    language = default_language
try:
    if language not in language_plugins:
        raise Exception("Plugin not found")
    language_plugins[language].load()
    language_plugin = language_plugins[language]
except Exception as e:
    raise
    print("Unable to load language plug-in '%s': %s\n" % (language, str(e)), file=sys.stderr)
    sys.exit(1)

# Parse rules file
rules_file = None
ir = None
form = LanguagePlugins.PluginOptions.DFA_IR
try:
    rules_file = RulesFile.parse(arguments.RULES_FILE, arguments.encoding)
    validator = RulesFile.Validator()
    traverser = RulesFile.Traverser(validator)
    rules_file.accept(traverser)
except Exception as e:
    print("Error parsing rules file. %s" % str(e), file=sys.stderr)
    sys.exit(1)

# Compile rules file
try:
    form = language_plugin.default_form
    if arguments.form != "default":
        if arguments.form == "nfa":
            form = LanguagePlugins.PluginOptions.NFA_IR
        elif arguments.form == "dfa":
            form = LanguagePlugins.PluginOptions.DFA_IR
    if form not in language_plugin.forms:
        raise Exception("Specified state machine form '{0}' not supported by language plugin".format(arguments.form))
    ir = RulesFile.NonDeterministicIR(rules_file)
    if form == LanguagePlugins.PluginOptions.DFA_IR:
        ir = RulesFile.DeterministicIR(ir)

except Exception as e:
    raise
    print("Error processing rules. %s" % str(e), file=sys.stderr)
    sys.exit(1)
    
# Emit output
try:
    plugin_options = LanguagePlugins.PluginOptions()
    plugin_options.class_name = arguments.class_name
    plugin_options.namespace = arguments.namespace
    plugin_options.file_name = arguments.file_name
    plugin_options.form = form
    
    emitter = language_plugin.create(ir, plugin_options)
    if os.path.normcase(os.path.realpath(arguments.OUTPUT_DIR)) == this_folder:
        print("Output directory cannot be same as executable directory", file=sys.stderr)
        sys.exit(1)
    executor = LanguagePlugins.Executor(emitter, language_plugin.plugin_files_directory, arguments.OUTPUT_DIR)
    executor.execute()
        
except IOError as e:
    print("Unable to write to output directory because of an error", file=sys.stderr)
    sys.exit(1)
    
except Exception as e:
    print("Unable to create lexical analyzer: %s" % str(e))
    sys.exit(1)
