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

class PluginTemplateNotImplemented(Exception):
    def __init__(self):
        Exception.__init__(self, "Not implemented")
    
class PluginTemplate(object):
    """
    Template from which language emitter plug-ins should derive
    """
    def __init__(self, lexical_analyzer, plugin_files, output_directory):
        """
        @param lexical_analyzer: a LexicalAnalyzer object representing the lexical analyzer to emit
        @param plugin_files: a string specifying the location of the plug-in's files
        @param output_directory: a string specifying the output directory where files should be saved
        """
        self.lexical_analyzer = lexical_analyzer
        self.plugin_files = plugin_files
        self.output_directory = output_directory
    
    def emit(self):
        """
        Emit all generated code
        """
        raise PluginTemplateNotImplemented()
    
    def get_output_directories(self):
        """
        Return a list of directories for Poodle-Lex to create in the output folder
        """
        raise PluginTemplateNotImplemented()
    
    def get_files_to_copy(self):
        """
        Return a list of files for Poodle-Lex to into the output directory
        """
        raise PluginTemplateNotImplemented()
