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

from abc import ABCMeta, abstractmethod

class TemplateToken(object):
    """
    Represents a single token in a single file
    @ivar filename: string containing the name of the file being generated
    @ivar stream: file object with which to write the stream output
    @ivar token: string containing the name of the token to be processed
    @ivar indent: integer containing the number of spaces preceding the token, 
        or None if the token is not at the start of the line
    """
    def __init__(self, filename):
        self.filename = filename
        self.stream = None
        self.token = None
        self.indent = None

class PluginTemplate(object):
    """
    Abstract class from which language emitter plug-ins should derive
    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def process(self, token):
        """
        Emit substituted text for a single token in a template file. This is called 
        for each instance of a token in each generated file
        @param token: TemplateToken object representing the token to be processed
        """
        pass
        
    @abstractmethod        
    def get_output_directories(self):
        """
        Return a list of strings, each the relative path to a directory for 
        Poodle-Lex to create in the output folder.
        """
        pass
        
    def get_files_to_copy(self):
        """
        Return a list of strings, each containing the relative path to a file 
        for Poodle-Lex to into the output directory.
        """
        pass
        
    def get_files_to_generate(self):
        """
        Specify files to generate using token replacement.
        @return: a list of tuples, each with two elements and representing a  
            file to be generated. The first element of each tuple is a string 
            containing the path to the template file from which to generate, 
            relative to the plugin's template folder. The second is a string 
            containing the path to the file which is to be generated, relative 
            to the output path.        
        """
        pass
        