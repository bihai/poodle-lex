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

from Emitter import PluginTemplate
import re
import json
import os.path
import random
import string
import imp

class Plugin(object):
    """
    Class representing a Poodle-Lex language emitter plug-in
    """
    def __init__(self, source_path, plugin_files_directory): 
        self.source_path = source_path
        self.plugin_files_directory = plugin_files_directory
        self.module = None
        
    def load(self):
        """
        Loads the plug-in and verifies the interface
        """
        with open(self.source_path, 'r') as f:
            modulename = "Generator.Emitter.language_plugin_%s" % ''.join(random.choice(string.ascii_lowercase) for i in range(16))
            self.module = imp.load_module(modulename, f, self.source_path, (".py", 'r', imp.PY_SOURCE))
        if not hasattr(self.module, 'LanguageEmitter') or not issubclass(self.module.LanguageEmitter, PluginTemplate.PluginTemplate):
            print type(self.module.LanguageEmitter)
            raise Exception("Plug-in does not contain a 'LanguageEmitter' class")
            
    def create(self, lexical_analyzer, output_directory):
        """
        Creates a LanugageEmitter object from the plug-in
        """
        if self.module is None:
            raise Exception("Plug-in not loaded")
        return self.module.LanguageEmitter(lexical_analyzer, self.plugin_files_directory, output_directory)
        
def is_text(text):
    """
    Simple utility function to determine if an object is of type str or unicode
    """
    return isinstance(text, str) or isinstance(text, unicode)
        
def load(base_directory, file, encoding='utf-8'):
    """ 
    Loads a plug-in file and returns 
    @param base_directory: string specifying the root directory of the application
    @param file: a string specifying the plug-in specification file
    @param encoding: a string specifying the encoding of the plug-in specification file
    @return: dict mapping strings representing plug-in identifiers to Plugin objects
    """
    language_plugins = {}
    default_language = None
    with open("Plugins/Plugins.json") as f:
        plugin_file = json.load(f, encoding)
        if "Version" not in plugin_file or not isinstance(plugin_file["Version"], int) or plugin_file["Version"] != 1:
            raise Exception("Language plug-in file version not recognized")
        if "Default" not in plugin_file or not is_text(plugin_file["Default"]):
            raise Exception("Default language not specified")
        default_language = plugin_file["Default"]
        if "Plugins" not in plugin_file or not isinstance(plugin_file["Plugins"], dict):
            raise Exception("Plugin dictionary not found")
        for plugin_id in plugin_file["Plugins"]:
            if is_text and re.match("[a-zA-Z][a-zA-Z0-9_\-\+]*", plugin_id):
                valid = True
                for plugin_attr in plugin_file["Plugins"][plugin_id]:
                    if is_text(plugin_attr) and plugin_attr in ("Source", "Files"):
                        if is_text(plugin_file["Plugins"][plugin_id][plugin_attr]):
                            if os.path.exists(plugin_file["Plugins"][plugin_id][plugin_attr]):
                                continue
                    valid = False
                if valid:
                    plugin_files_directory = plugin_file["Plugins"][plugin_id]["Files"]
                    if not os.path.isabs(plugin_files_directory):
                        plugin_files_directory = os.path.join(base_directory, plugin_files_directory)
                    language_plugins[plugin_id] = Plugin(plugin_file["Plugins"][plugin_id]["Source"], plugin_files_directory)
       
        if len(language_plugins) == 0:
            raise Exception("No plugins found")
        if plugin_file["Default"] not in language_plugins:
            raise Exception("Default language is invalid")
    return language_plugins, default_language