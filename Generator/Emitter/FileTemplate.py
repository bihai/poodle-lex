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

import re

def FileTemplate(in_filename, out_filename):
    """
    Helper class for filling in template files.
    Returns an iterator which copies a file's contents, pausing to yeild each time it hits a $VARIABLE token.
    Yields the following for each $VARIABLE token in the file:
        1. A Python file object representing the output file
        2. A string containing the name of the token
        3. If the token is the first non-whitespace of a line, an integer with the indentation, otherwise None.
    @param in_filename: string containing the name of the template file to copy
    @param out_filename: string containing the name of the filled-in template file to write.
    """
    pattern_variablename = r"\$(?P<%s>[a-zA-Z][a-zA-Z0-9_]*)"
    pattern_inline = pattern_variablename % "inline"
    pattern_entireline = r"^(?P<whitespace>[ \t]*)%s" % (pattern_variablename % "entireline")
    pattern_variable = r"(%s)|(%s)" % (pattern_entireline, pattern_inline)
    
    with open(in_filename, 'r') as in_file:
        with open(out_filename, 'w') as out_file:
            for line in in_file:
                match = re.search(pattern_variable, line)
                if match is not None:
                    if match.group('entireline') is not None:
                        yield out_file, match.group('entireline'), len(match.group('whitespace'))
                    else:
                        out_file.write(line[:match.start(0)])
                        yield out_file, match.group('inline'), None
                        out_file.write(line[match.end(0):])
                else:
                    out_file.write(line)
                    