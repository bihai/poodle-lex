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
from Generator.Emitter.FreeBasic import FreeBasic
from Generator.RegexParser import RegexParser
from Generator.RegexExceptions import *
import argparse
import re
import sys
import shutil
import os
import os.path

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("RULES_FILE", help="Rules file")
arg_parser.add_argument("OUTPUT_DIR", help="Containing directory for output files")
arg_parser.add_argument("-n", "--print-nfa", help="Print a graph of the NFA of the ruleset to a .dot file", metavar="DOT_FILE")
arg_parser.add_argument("-d", "--print-dfa", help="Print a graph of the non-minimized DFA of the ruleset to a .dot file", metavar="DOT_FILE")
arg_parser.add_argument("-m", "--print-min-dfa", help="Print a graph of the minimized DFA of the ruleset to a .dot file", metavar="DOT_FILE")
arguments = arg_parser.parse_args()

# Copy non-generated files over
try:
    this_folder = os.path.dirname(os.path.normcase(os.path.realpath(__file__)))
    dirs = [
        ("Test",),
        ("Stream",),
        ("Stream", "Windows"),
        ("Stream", "Linux")
    ]
    files = [
        ("Stream", "Windows", "MemoryMapWindows.bas"),
        ("Stream", "Windows", "MemoryMapWindows.bi"),
        ("Stream", "Linux", "MemoryMapLinux.bas"),
        ("Stream", "Linux", "MemoryMapLinux.bi"),
        ("Stream", "ASCIIStream.bas"),
        ("Stream", "ASCIIStream.bi"),
        ("Stream", "CharacterStream.bas"),
        ("Stream", "CharacterStream.bi"),
        ("Stream", "CharacterStreamFromFile.bas"),
        ("Stream", "CharacterStreamFromFile.bi"),
        ("Stream", "MemoryMap.bas"),
        ("Stream", "MemoryMap.bi"),
        ("Stream", "Unicode.bas"),
        ("Stream", "Unicode.bi"),
        ("Stream", "UnicodeConstants.bas"),
        ("Stream", "UnicodeConstants.bi"),
        ("Stream", "UTF8Stream.bas"),
        ("Stream", "UTF8Stream.bi"),
        ("Stream", "UTF16Stream.bas"),
        ("Stream", "UTF16Stream.bi"),
        ("Stream", "UTF32Stream.bas"),
        ("Stream", "UTF32Stream.bi"),
        ("Test", "Test.bas"),
        ("Test", "Test.txt"),
        ("Test", "make_test.bat"),
        ("Test", "make_test.sh")
    ]
    if not os.path.exists(arguments.OUTPUT_DIR):
        sys.stderr.write("Output directory not found\n")
        exit()
    if os.path.normcase(os.path.realpath(arguments.OUTPUT_DIR)) == this_folder:
        sys.stderr.write("Output directory cannot be same as executable directory\n")
        exit()
    for dirname in dirs:
        if not os.path.exists(os.path.join(arguments.OUTPUT_DIR, *dirname)):
            os.mkdir(os.path.join(arguments.OUTPUT_DIR, *dirname))
    for file in files:
        shutil.copy(os.path.join(this_folder, *file), os.path.join(arguments.OUTPUT_DIR, *file))
except IOError:
    sys.stderr.write("Unable to write to output directroy because of an error\n")
    exit()

try:
    lexer = LexicalAnalyzer.parse(arguments.RULES_FILE)
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
    
    FreeBasic(lexer).emit(*[os.path.join(arguments.OUTPUT_DIR, i) for i in "LexicalAnalyzer.bi", "LexicalAnalyzer.bas"])

except RegexParserException as e:
    sys.stderr.write("Unable to parse rule '%s': %s\n" % (e.rule_id, e.message))

except LexicalAnalyzerParserException as e:
    sys.stderr.write("Error parsing rules file: %s\n" % e.message)

