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

from ..Emitter.PluginTemplate import PluginTemplate
import os.path
import random
import string
import imp
import sys
import textwrap
import types
import Parser

def rethrow_formatted(e, action):
    """
    Format errors that occur from within plugin with line number and filename
    @param e: an exception object to re-throw
    @param action: string identifier describing what the program was doing when the exception was thrown
    """
    exception_type, exception_object, exception_traceback = sys.exc_info()
    while exception_traceback.tb_next != None:
        exception_traceback = exception_traceback.tb_next
    filename = os.path.split(exception_traceback.tb_frame.f_code.co_filename)[1]
    raise Exception("In '{filename}', line {line}, while {action}, {error}".format(
        filename=filename,
        line=exception_traceback.tb_lineno,
        action=action,
        error=str(e)))

class PluginOptions(object):
    def __init__(self):
        self.is_backtracking = False
        self.class_name = None
        self.namespace = None
        self.file_name = None
        
class Plugin(object):
    """
    Class representing a Poodle-Lex language emitter plug-in
    @ivar source_path: String containing the path to the main plugin file 
        containing create_emitter()
    @ivar plugin_files_directory: String containing path to the plugin files
    @ivar description: String describing the plugin
    """
    def __init__(self, source_path, plugin_files_directory, dependencies, description): 
        self.source_path = source_path
        self.plugin_files_directory = plugin_files_directory
        self.description = description
        self.dependencies = dependencies
        self.module = None
        self.dependency_modules = {}
        
    def load(self):
        """
        Loads the plug-in and verifies the interface
        """
        for dependency in self.dependencies:
            with open(dependency, 'r') as f:
                module_name = os.path.splitext(os.path.basename(dependency))[0]
                path_template = "Generator.Emitter.language_plugin_dependency_%s_%s"
                module_path = path_template % (module_name, ''.join(random.choice(string.ascii_lowercase) for i in range(8)))
                self.dependency_modules[module_name] = imp.load_module(module_path, f, dependency, (".py", 'r', imp.PY_SOURCE))
        with open(self.source_path, 'r') as f:
            module_path = "Generator.Emitter.language_plugin_%s" % ''.join(random.choice(string.ascii_lowercase) for i in range(16))
            self.module = imp.load_module(module_path, f, self.source_path, (".py", 'r', imp.PY_SOURCE))
        if not hasattr(self.module, 'create_emitter') or not isinstance(self.module.create_emitter, types.FunctionType):
            raise Exception("Plug-in does not contain a 'create_emitter' function")
            
    def create(self, lexical_analyzer, plugin_options):
        """
        Creates a LanugageEmitter object from the plug-in
        """
        if self.module is None:
            raise Exception("Plug-in not loaded")
        try:
            emitter = self.module.create_emitter(lexical_analyzer, self.dependency_modules, plugin_options)
        except Exception as e:
            rethrow_formatted(e, 'while initializing language plugin')
        if not issubclass(emitter.__class__, PluginTemplate):
            raise Exception("Plug-in interface did not return a class of the correct type")
        return emitter
                                        
def describe(base_folder, file, encoding):
    language_plugins, default_language = Parser.load(base_folder, file, encoding)
    left_column_size = len(max(language_plugins, key=lambda i: len(i))) + 1
    sys.stderr.write("Available output languages:\n")
    for language, plugin in language_plugins.iteritems():
        paragraph = textwrap.wrap(plugin.description, 76-left_column_size)
        sys.stderr.write("    %s%s%s\n" % (language, ' '*(left_column_size-len(language)), paragraph[0]))
        if len(paragraph) > 1:
            for line in paragraph[1:]:
                sys.stderr.write("    %s%s\n" % (' '*left_column_size, line))
    
