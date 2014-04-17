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

import os.path
import platform
from cx_Freeze import setup,Executable

includefiles = [
    os.path.join('Plugins', 'Plugins.json'),
    os.path.join('Plugins', 'FreeBasic', 'FreeBasic.py'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'LexicalAnalyzer.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'LexicalAnalyzer.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'Windows', 'MemoryMapWindows.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'Windows', 'MemoryMapWindows.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'Linux', 'MemoryMapLinux.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'Linux', 'MemoryMapLinux.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'MemoryMap.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'MemoryMap.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'Unicode.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'Unicode.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'UnicodeConstants.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'UnicodeConstants.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'UTF8Stream.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'UTF8Stream.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'UTF16Stream.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'UTF16Stream.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'UTF32Stream.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'UTF32Stream.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'ASCIIStream.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'ASCIIStream.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'CharacterStream.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'CharacterStream.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'CharacterStreamFromFile.bas'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Stream', 'CharacterStreamFromFile.bi'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Demo', 'make_demo.bat'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Demo', 'make_demo.sh'),
    os.path.join('Plugins', 'FreeBasic', 'Template', 'Demo', 'Demo.bas'),
    os.path.join('Plugins', 'CPlusPlus', 'CPlusPlus.py'),
    os.path.join('Plugins', 'CPlusPlus', 'Template', 'lexical_analyzer.c'),
    os.path.join('Plugins', 'CPlusPlus', 'Template', 'lexical_analyzer.h'),
    os.path.join('Plugins', 'CPlusPlus', 'Template', 'demo', 'demo.c'),
    os.path.join('Plugins', 'CPlusPlus', 'Template', 'demo', 'make_demo.sh'),
    os.path.join('Plugins', 'CPlusPlus', 'Template', 'demo', 'make_demo.bat'),
    os.path.join('Example', 'CPlusPlus', 'CLexer.rules'),
    os.path.join('Example', 'CPlusPlus', 'HelloWorld.c'),
    os.path.join('Example', 'SimpleLexer', 'SimpleLexer.rules'),
    os.path.join('Example', 'SimpleLexer', 'SimpleLexerText.txt'),
    'README',
    'LICENSE',
    'CHANGELIST'
]
includes = []
excludes = []
packages = ['blist']
target_name = "Poodle-Lex"
if platform.system() == "Windows":
    target_name += ".exe"
setup(
    name = 'Poodle-Lex',
    version = '1.0',
    description = 'A lexical analyzer generator with support for multiple languages.',
    author = 'Parker Michaels',
    author_email = 'parkertomatoes@gmail.com',
    options = {
        'build_exe': {
            'excludes':excludes,
            'packages':packages,
            'include_files':includefiles
        },
        'bdist_msi': {
            'upgrade_code': '{d7bbdad8-411a-4662-bc31-f5494b9cd11f}'
        }
    }, 
    executables = [Executable('__main__.py', targetName=target_name)]
)
