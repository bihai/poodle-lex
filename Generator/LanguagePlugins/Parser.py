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
import os.path
import json
import LanguagePlugins

def is_text(text):
    """
    Simple utility function to determine if an object is of type str or unicode
    """
    return isinstance(text, str) or isinstance(text, unicode)
    
def is_path(text, base_directory):
    """
    Simple utility function to determine if the object is an str, and represents a valid path
    @return: a string with the resolved path, or None if not a path
    """
    if is_text(text):
        if not os.path.isabs(text):
            path = os.path.join(base_directory, text)
        else:
            path = text
        if os.path.exists(path):
            return path
    return None
    
def is_form(form):
    """
    Simple utility function to check valid entries for "Forms" and "DefaultForm"
    @return: The specified state machine representation, in enum form.
    """
    if is_text(form):
        if form.lower() == "dfa":
            return LanguagePlugins.PluginOptions.DFA_IR
        elif form.lower() == "nfa":
            return LanguagePlugins.PluginOptions.NFA_IR
    return None

def load(file, encoding='utf-8'):
    """ 
    Loads a plug-in file and returns 
    @param file: a string specifying the plug-in specification file
    @param encoding: a string specifying the encoding of the plug-in specification file
    @return: dict mapping strings representing plug-in identifiers to Plugin objects
    """
    language_plugins = {}
    default_language = None
    if not os.path.exists(file):
        raise Exception("Plugin file not found")
    base_directory = os.path.dirname(file)
    with open(file) as f:
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
                plugin_paths = {}
                dependencies = []
                description = ""
                forms = [LanguagePlugins.PluginOptions.DFA_IR]
                default_form = LanguagePlugins.PluginOptions.DFA_IR
                for plugin_attr in plugin_file["Plugins"][plugin_id]:
                    if is_text(plugin_attr) and plugin_attr in ("Source", "Files"):
                        plugin_paths[plugin_attr] = is_path(plugin_file["Plugins"][plugin_id][plugin_attr], base_directory)
                        if plugin_paths[plugin_attr] is None:
                            valid = False
                    elif plugin_attr == "Dependencies":
                        raw_dependencies = plugin_file["Plugins"][plugin_id][plugin_attr]
                        if not isinstance(raw_dependencies, list):
                            valid = False
                        dependencies = [is_path(i, base_directory) for i in raw_dependencies]
                        if any(i is None for i in dependencies):   
                            valid = False
                    elif plugin_attr == "Description":
                        if is_text(plugin_file["Plugins"][plugin_id][plugin_attr]):
                            description = plugin_file["Plugins"][plugin_id][plugin_attr]
                        else:
                            valid = False
                    elif plugin_attr == "Forms":
                        pf_forms = plugin_file["Plugins"][plugin_id][plugin_attr]
                        if isinstance(pf_forms, list):
                            forms = set()
                            for form in pf_forms:
                                parsed_form = is_form(form)
                                if parsed_form is not None:
                                    forms.add(parsed_form)
                    elif plugin_attr == "DefaultForm":
                        pf_default_form = is_form(plugin_file["Plugins"][plugin_id][plugin_attr])
                        if pf_default_form is not None:
                            default_form = pf_default_form
                if default_form not in forms:
                    valid = False
                if "Source" not in plugin_paths or "Files" not in plugin_paths:
                    valid = False
                if valid:
                    language_plugins[plugin_id] = LanguagePlugins.Plugin(
                        plugin_paths["Source"], 
                        plugin_paths["Files"], 
                        dependencies,
                        description,
                        forms,
                        default_form)
       
        if len(language_plugins) == 0:
            raise Exception("No plugins found")
        if plugin_file["Default"] not in language_plugins:
            raise Exception("Default language is invalid")
    return language_plugins, default_language
