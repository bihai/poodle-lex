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
    os.path.join('Template', 'FreeBasic', 'LexicalAnalyzer.bas'),
    os.path.join('Template', 'FreeBasic', 'LexicalAnalyzer.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'Windows', 'MemoryMapWindows.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'Windows', 'MemoryMapWindows.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'Linux', 'MemoryMapLinux.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'Linux', 'MemoryMapLinux.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'MemoryMap.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'MemoryMap.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'Unicode.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'Unicode.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'UnicodeConstants.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'UnicodeConstants.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'UTF8Stream.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'UTF8Stream.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'UTF16Stream.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'UTF16Stream.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'UTF32Stream.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'UTF32Stream.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'ASCIIStream.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'ASCIIStream.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'CharacterStream.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'CharacterStream.bi'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'CharacterStreamFromFile.bas'),
    os.path.join('Template', 'FreeBasic', 'Stream', 'CharacterStreamFromFile.bi'),
    os.path.join('Template', 'FreeBasic', 'Demo', 'make_demo.bat'),
    os.path.join('Template', 'FreeBasic', 'Demo', 'make_demo.sh'),
    os.path.join('Template', 'FreeBasic', 'Demo', 'Demo.bas'),
    os.path.join('Example', 'CLexer', 'CLexer.rules'),
    os.path.join('Example', 'CLexer', 'HelloWorld.c'),
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
    version = '0.9',
    description = 'A lexical analyzer generator which emits FreeBASIC code',
    author = 'Parker Michaels',
    author_email = 'parkertomatoes@gmail.com',
    options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}}, 
    executables = [Executable('__main__.py', targetName=target_name)]
)
