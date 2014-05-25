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

from Emitter.FileTemplate import FileTemplate, TemplateToken
import shutil
import os.path
import os

class Executor(object):
    def __init__(language_plugin, template_directory, output_directory)
        self.language_plugin = language_plugin
        self.template_directory = template_directory
        self.output_directory = output_directory
        
    def create_directories(self):
        if not os.path.exists(self.output_directory):
            raise Exception("Output directory not found")

        for directory_name in self.language_plugin.get_output_directories():
            real_directory_name = os.path.join(self.output_directory, directory_name)
            if not os.path.exists(real_directory_name):
                os.mkdir(real_directory_name)

    def copy_files(self):
        for file in self.language_plugin.get_files_to_copy():
            shutil.copy(os.path.join(self.language_plugin.template_directory, file), os.path.join(self.output_directory, file))

    def generate_files(self):
        for template_file, output_file in self.language_plugin.get_files_to_generate():
            real_template_file = os.path.join(self.template_directory, template_file)
            real_output_file = os.path.join(self.output_directory, output_file)
            template_token = TemplateToken(template_file)
            for stream, token, indent in FileTemplate(real_template_file, real_output_file):
                template_token.token = token
                template_token.stream = stream
                template_token.indent = indent
                language_plugin.process(template_token)
                