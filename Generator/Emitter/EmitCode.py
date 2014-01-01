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

class CodeEmitter(object):
    """
    A helper class for writing indented lines to a file.
    @ivar indent_size: integer representing the current indentation
    @ivar stream: Python file object to which lines should be written
    """
    def __init__(self, stream=None):
        """
        @param stream: Python file object to which lines should be written.
        """
        self.indent_size = 0
        self.stream = stream
        
    def indent(self):
        """
        Increases the current indentation by four spaces.
        """
        self.indent_size += 4
        
    def dedent(self):
        """
        Decreases the current indentation by four spaces.
        """
        self.indent_size -= 4
        
    def open_line(self):    
        """
        Start a new, indented line.
        """
        self.write(' '*self.indent_size)
    
    def close_line(self):
        """
        End an indented line.
        """
        self.write('\n')
        
    def write(self, text):
        """
        Write text to the stream
        @param text: string containg the text to write to the stream
        """
        self.stream.write(text)
        
    def line(self, text=""):
        """
        Write a single indented line at once.
        @param text: string containing the contents of the line.
        """
        lines = text.split("\n")
        for line in lines:
            self.open_line()
            self.write(line)
            self.close_line()
        
    def inherit(self, parent):
        """
        Start using the stream from another CodeEmitter object
        @param parent: another CodeEmitter object from which to inherit.
        """
        self.stream = parent.stream
        self.indent_size = parent.indent_size

