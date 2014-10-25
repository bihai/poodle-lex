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

import sys
import argparse

class Command(object):
    def __init__(self, type, arguments):
        self.type = type
        self.arguments = arguments

def handle():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list-minimizers':
            return 'list-minimizers', None
        if sys.argv[1] == 'list-languages':
            return 'list-languages', None
        if sys.argv[1] == 'list-forms':
            return 'list-forms', None
    
    # Parse complex options
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("RULES_FILE", help="Rules file")
    arg_parser.add_argument("OUTPUT_DIR", help="Containing directory for output files")
    arg_parser.add_argument("-e", "--encoding", help="Rules file encoding", default="utf-8")
    arg_parser.add_argument("-i", "--minimizer", help="Minimizer algorithm to use. Use '--action=list-minimizers' for list of options", default="hopcroft", metavar="ALGORITHM")
    arg_parser.add_argument("-l", "--language", help="Output programming language. Use '--action=list-languages' for list of options", default=None)
    arg_parser.add_argument("-m", "--form", help="The type of state machine to use. Use '--action-list-forms' for list of options'", default='default', choices=['nfa', 'dfa', 'default'])
    arg_parser.add_argument("-c", "--class-name", help="The name of the lexical analyzer class to generate", default=None)
    arg_parser.add_argument("-f", "--file-name", help="The base name of the generated source files", default=None)
    arg_parser.add_argument("-s", "--namespace", help="The namespace name of the lexical analyzer class to generate", default=None)
    arguments = arg_parser.parse_args()

    return 'build', arguments
    