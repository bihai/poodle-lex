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
    
    class Block(object):
        """
        Object which hides some boilerplate code for writing indented 
        blocks behind python's "with" statement
        """
        def __init__(self, emitter, opening_line, closing_line):
            self.emitter = emitter
            self.opening_line = opening_line
            self.closing_line = closing_line
            
        def __enter__(self):
            self.emitter.line(opening_line)
            self.emitter.indent()
        
        def __exit__(self):
            self.emitter.dedent()
            self.emitter.line(closing_line)
        
    def __init__(self, stream=None, initial_indent=0, indent_spaces=4):
        """
        @param stream: Python file object to which lines should be written.
        """
        self.indent_size = initial_indent*indent_spaces
        self.indent_spaces = indent_spaces
        self.stream = stream
        
    def indent(self):
        """
        Increases the current indentation
        """
        self.indent_size += self.indent_spaces
        
    def dedent(self):
        """
        Decreases the current indentation
        """
        self.indent_size -= self.indent_spaces
        
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
            
    def block(self, opening_line, closing_line):
        """
        Returns an object for use with Python's "with" statement. Code
        printed inside the with statement will be indented and wrapped
        in opening and closing lines.
        @param opening_line: The text at the head of the block (such as "do" or "if")
        @param closing_line: The text at the tail of the block (such as "loop" or "end if")
        """
        return Block(self, opening_line, closing_line)
        
    def continue_block(self, *lines):
        """
        For use inside "with code.block()" sections, this method ends the 
        current block body and starts another. Useful, for instance, with
        "if, then else" statements with multiple bodies.
        @param line: Lines of text to divide the two sections
        """
        self.dedent()
        for line_of_code in lines:
            self.line(line_of_code)
        self.indent()
        
    def inherit(self, parent):
        """
        Start using the stream from another CodeEmitter object
        @param parent: another CodeEmitter object from which to inherit.
        """
        self.stream = parent.stream
        self.indent_size = parent.indent_size

