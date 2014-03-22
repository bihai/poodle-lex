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

from Generator.LexicalAnalyzerParser import LexicalAnalyzerParserException
from Generator.LexicalAnalyzer import LexicalAnalyzer
from Generator.RegexParser import RegexParser
from Generator.RegexExceptions import *
from Generator import NaiveDFAMinimizer
from Generator import HopcroftDFAMinimizer
from Generator import LanguagePlugins
import argparse
import sys
import shutil
import os
import os.path

this_file = sys.executable
if getattr(sys, 'frozen', None) is None:
    this_file = __file__
this_folder = os.path.dirname(os.path.normcase(os.path.realpath(this_file)))


# Use simple command parsing for simple commands
minimizers = {
    'hopcroft': ('Minimize using Hopcroft\'s partition refinement algorithm', HopcroftDFAMinimizer.minimize),
    'polynomial': ('Minimize using a polynomial algorithm comparing each state', NaiveDFAMinimizer.minimize)
}
if len(sys.argv) > 1 and sys.argv[1] == 'list-minimizers':
    left_column_size = len(max(minimizers, key=lambda i: len(i))) + 1
    sys.stderr.write("Supported DFA minimization algorithms:\n")
    for name, (description, minimizer) in minimizers.iteritems():
        sys.stderr.write("    %s%s%s\n" % (name, ' '*(left_column_size-len(name)), description))
    sys.exit(0)

# Load language plug-ins file and list languages if requested
language_plugins = None
default_language = None
try:
    if len(sys.argv) > 1 and sys.argv[1] == 'list-languages':
        LanguagePlugins.describe(this_folder, "Plugins/Plugins.json", 'utf-8')
        sys.exit(0)
    else:
        language_plugins, default_language = LanguagePlugins.load(this_folder, "Plugins/Plugins.json", 'utf-8')
except Exception as e: 
   sys.stderr.write("Unable to load plug-in file: %s\n" % str(e))
   sys.exit()

# Parse complex options
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("RULES_FILE", help="Rules file")
arg_parser.add_argument("OUTPUT_DIR", help="Containing directory for output files")
arg_parser.add_argument("-e", "--encoding", help="Rules file encoding", default="utf-8")
arg_parser.add_argument("-n", "--print-nfa", help="Print a graph of the NFA of the ruleset to a .dot file", metavar="DOT_FILE")
arg_parser.add_argument("-d", "--print-dfa", help="Print a graph of the non-minimized DFA of the ruleset to a .dot file", metavar="DOT_FILE")
arg_parser.add_argument("-m", "--print-min-dfa", help="Print a graph of the minimized DFA of the ruleset to a .dot file", metavar="DOT_FILE")
arg_parser.add_argument("-i", "--minimizer", help="Minimizer algorithm to use. Use '--action=list-minimizers' for list of options", default="hopcroft", metavar="ALGORITHM")
arg_parser.add_argument("-l", "--language", help="Output programming language. Use '--action=list-languages' for list of options", default=None)
arguments = arg_parser.parse_args()

# Check minimizer
if arguments.minimizer not in minimizers:
    sys.stderr.write("Minimizer '%s' not recognized\n" % arguments.minimizer)
    sys.exit()
minimizer_description, minimizer = minimizers[arguments.minimizer]

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
    sys.stderr.write("Unable to load language plug-in '%s': %s\n" % (language, str(e)))
    sys.exit()    

try:
    lexer = LexicalAnalyzer.parse(arguments.RULES_FILE, arguments.encoding, minimizer=minimizer)
    lexer.finalize()
    
    # Export automata if requested
    if arguments.print_nfa is not None:
        try:
            with open(arguments.print_nfa, 'w') as f:
                f.write(repr(lexer.get_nfa()))
        except IOError:
            sys.stderr.write("Unable to open nfa .dot file\n")

    if arguments.print_dfa is not None:
        try:            
            with open(arguments.print_dfa, 'w') as f:
                f.write(repr(lexer.get_dfa()))
        except IOError:
            sys.stderror.write("Unable to open minimized dfa .dot file\n")
            
    if arguments.print_min_dfa is not None:
        try:            
            with open(arguments.print_min_dfa, 'w') as f:
                f.write(repr(lexer.get_min_dfa()))
        except IOError:
            sys.stderror.write("Unable to open minimized dfa .dot file\n")
except RegexParserException as e:
    sys.stderr.write("Unable to parse rule '%s': %s\n" % (e.rule_id, e.message))
    sys.exit()
    
except LexicalAnalyzerParserException as e:
    sys.stderr.write("Error parsing rules file: %s\n" % e.message)
    sys.exit()
    
except Exception as e:
    sys.stderr.write("Internal error while generating the lexical analyzer: %s" % str(e))
    sys.exit()    

# Copy non-generated files over
try:
    emitter = language_plugin.create(lexer, arguments.OUTPUT_DIR)
    
    if not os.path.exists(arguments.OUTPUT_DIR):
        sys.stderr.write("Output directory not found\n")
        sys.exit()
    if os.path.normcase(os.path.realpath(arguments.OUTPUT_DIR)) == this_folder:
        sys.stderr.write("Output directory cannot be same as executable directory\n")
        sys.exit()
    
    for directory_name in emitter.get_output_directories():
        real_directory_name = os.path.join(arguments.OUTPUT_DIR, directory_name)
        if not os.path.exists(real_directory_name):
            os.mkdir(real_directory_name)
            
    for file in emitter.get_files_to_copy():
        shutil.copy(os.path.join(language_plugin.plugin_files_directory, file), os.path.join(arguments.OUTPUT_DIR, file))
        
except IOError as e:
    sys.stderr.write("Unable to write to output directory because of an error\n")
    raise e
    sys.exit()
    
try:
    emitter.emit()
except Exception as e:
    sys.stderr.write("An error occured while emitting code: '%s'" % str(e))
