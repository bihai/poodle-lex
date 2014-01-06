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
from cx_Freeze import setup,Executable

includefiles = [
    os.path.join('Generator', 'Emitter', 'Template', 'LexicalAnalyzer.bas'),
    os.path.join('Generator', 'Emitter', 'Template', 'LexicalAnalyzer.bi'),
    os.path.join('Stream', 'MemoryMap.bas'),
    os.path.join('Stream', 'MemoryMap.bi'),
    os.path.join('Stream', 'Unicode.bas'),
    os.path.join('Stream', 'Unicode.bi'),
    os.path.join('Stream', 'UnicodeConstants.bas'),
    os.path.join('Stream', 'UnicodeConstants.bi'),
    os.path.join('Stream', 'UTF8Stream.bas'),
    os.path.join('Stream', 'UTF8Stream.bi'),
    os.path.join('Stream', 'UTF16Stream.bas'),
    os.path.join('Stream', 'UTF16Stream.bi'),
    os.path.join('Stream', 'UTF32Stream.bas'),
    os.path.join('Stream', 'UTF32Stream.bi'),
    os.path.join('Stream', 'ASCIIStream.bas'),
    os.path.join('Stream', 'ASCIIStream.bi'),
    os.path.join('Stream', 'CharacterStream.bas'),
    os.path.join('Stream', 'CharacterStream.bi'),
    os.path.join('Stream', 'CharacterStreamFromFile.bas'),
    os.path.join('Stream', 'CharacterStreamFromFile.bi'),
    os.path.join('Test', 'Test.txt'),
    os.path.join('Test', 'make_test.bat'),
    os.path.join('Test', 'make_test.sh'),
    os.path.join('Test', 'Test.bas'),
    os.path.join('Test', 'Test.rules'),
    'README',
    'LICENSE'
]
includes = []
excludes = []
packages = ['blist']

setup(
    name = 'Poodle-Lex',
    version = '0.5',
    description = 'A lexical analyzer generator which emits FreeBASIC code',
    author = 'Parker Michaels',
    author_email = 'parkertomatoes@gmail.com',
    options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}}, 
    executables = [Executable('__main__.py', targetName="Poodle-Lex.exe")]
)
