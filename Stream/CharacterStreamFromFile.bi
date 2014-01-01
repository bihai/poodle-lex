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

#ifndef POODLE_CHARACTERSTREAMFROMFILE_BI
#define POODLE_CHARACTERSTREAMFROMFILE_BI

#include "MemoryMap.bi"
#include "CharacterStream.bi"

Namespace Poodle
    '' Base class for encoding streams
    Type CharacterStreamFromFile Extends CharacterStream
        Public:
        Declare Constructor()
        Declare Constructor(Filename As String)
        Declare Constructor(ByVal CharacterData As Unsigned Byte Pointer, ByVal SizeInBytes As Unsigned LongInt)
        Declare Virtual Function IsEndOfStream() As Integer
        Declare Virtual Function GetStatus() As CharacterStream.CharacterStreamStatus
        Declare Virtual Destructor()
        
        Protected:
        FileMap As MemoryMap Pointer
        CharacterData As Unsigned Byte Pointer
        Status As CharacterStream.CharacterStreamStatus
        Size As Unsigned LongInt
        Index As Unsigned LongInt
    End Type
End Namespace

#endif
