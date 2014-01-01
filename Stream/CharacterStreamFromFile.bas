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

#include "MemoryMap.bi"
#include "CharacterStreamFromFile.bi"

Constructor Poodle.CharacterStreamFromFile()
    This.FileMap = 0
    This.Size = 0
    This.Index = 0
    This.Status = Poodle.CharacterStream.CharacterStreamInvalid
End Constructor

Constructor Poodle.CharacterStreamFromFile(Filename As String)
    This.FileMap = Poodle.MemoryMap.Open(Filename)
    If This.FileMap->GetStatus() <> Poodle.MemoryMap.MemoryMapValid Then
        This.Status = Poodle.CharacterStream.CharacterStreamInvalid
        This.Size = 0
        This.Index = 0
        Exit Constructor
    End If
    
    This.Size = This.FileMap->GetSize()
    This.Status = Poodle.CharacterStream.CharacterStreamValid
    This.CharacterData = This.FileMap->GetData()
    This.Index = 0
End Constructor

Constructor Poodle.CharacterStreamFromFile(CharacterData As Unsigned Byte Pointer, SizeInBytes As Unsigned LongInt)
    This.FileMap = 0
    This.CharacterData = CharacterData
    This.Size = SizeInBytes
    This.Index = 0
    If CharacterData = 0 Then
        This.Status = Poodle.CharacterStream.CharacterStreamValid
    Else
        This.Size = 0
        This.Status = Poodle.CharacterStream.CharacterStreamInvalid
    End If
End Constructor

Function Poodle.CharacterStreamFromFile.IsEndOfStream() As Integer
    If This.Index >= This.Size Or This.Status = Poodle.CharacterStream.CharacterStreamInvalid Then
        Return -1
    Else 
        Return 0
    End If
End Function

Function Poodle.CharacterStreamFromFile.GetStatus() As Poodle.CharacterStream.CharacterStreamStatus
    Return This.Status
End Function

Destructor Poodle.CharacterStreamFromFile()
    If This.FileMap <> 0 Then
        Delete This.FileMap
        This.FileMap = 0
    End If
End Destructor
