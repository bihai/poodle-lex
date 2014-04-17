' Copyright (C) 2014 Parker Michaels
' 
' Permission is hereby granted, free of charge, to any person obtaining a 
' copy of this software and associated documentation files (the "Software"), 
' to deal in the Software without restriction, including without limitation 
' the rights to use, copy, modify, merge, publish, distribute, sublicense, 
' and/or sell copies of the Software, and to permit persons to whom the 
' Software is furnished to do so, subject to the following conditions:
' 
' The above copyright notice and this permission notice shall be included in 
' all copies or substantial portions of the Software.
' 
' THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
' IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
' FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
' AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
' LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
' FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
' DEALINGS IN THE SOFTWARE.

#ifndef POODLE_UNICODETEXTSTREAM_BI
#define POODLE_UNICODETEXTSTREAM_BI

#include "CharacterStream.bi"
#include "Unicode.bi"

Namespace Poodle
    '' Streams UTF-8 characters from a file
    Type UnicodeTextStream Extends CharacterStream
        Public:
        Declare Constructor()
        Declare Constructor(ByRef As Unicode.Text)
        Declare Virtual Function IsEndOfStream() As Integer
        Declare Virtual Function GetStatus() As CharacterStreamStatus
        Declare Virtual Function GetCharacter() As Unicode.Codepoint
        Declare Virtual Destructor()
        
        Private:
        Text As Unicode.Text
        Index As Unsigned Integer
    End Type
End Namespace

#endif
