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

#include "ASCIIStream.bi"
#include "UnicodeConstants.bi"

Constructor Poodle.ASCIIStream(Filename As String)
    Base(Filename)
End Constructor

Constructor Poodle.ASCIIStream(CharacterData As Unsigned Byte Pointer, SizeInBytes As Unsigned LongInt)
    Base(CharacterData, SizeInBytes)
End Constructor

Function Poodle.ASCIIStream.GetCharacter() As Poodle.UnicodeCodepoint
    If This.Status = CharacterStream.CharacterStreamInvalid Then
        Return Poodle.UnicodeInvalidCharacter
    End If
    
    If This.Index >= This.Size Then
        Return Poodle.UnicodeNullCharacter
    End If
    
    This.Index += 1
    Return Cast(Integer, This.CharacterData[This.Index-1])
End Function
