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
#include "UTF32Stream.bi"
#include "UnicodeConstants.bi"

Constructor Poodle.UTF32Stream()
End Constructor

Constructor Poodle.UTF32Stream(Filename As String)
    Base(Filename)
    This.DetectByteOrder()
End Constructor

Constructor Poodle.UTF32Stream(CharacterData As Unsigned Byte Pointer, SizeInBytes As Unsigned LongInt)
    Base(CharacterData, SizeInBytes)
    This.DetectByteOrder()
End Constructor

Property Poodle.UTF32Stream.ByteOrder() As Poodle.UTF32Stream.ByteOrderType
    Return This.ByteOrderData
End Property

Property Poodle.UTF32Stream.ByteOrder(ByVal Order As Poodle.UTF32Stream.ByteOrderType)
    This.ByteOrderData = Order
End Property

Sub Poodle.UTF32Stream.DetectByteOrder()
    If This.Size < 4 Then 
        This.ByteOrderData = Poodle.UTF32Stream.UTF32BigEndian
    ElseIf _
        This.CharacterData[0] = Poodle.UTF16BigEndianMark(0) And _
        This.CharacterData[1] = Poodle.UTF16BigEndianMark(1) And _
        This.CharacterData[2] = Poodle.UTF16BigEndianMark(2) And _
        This.CharacterData[3] = Poodle.UTF16BigEndianMark(3) Then
        This.ByteOrderData = Poodle.UTF32Stream.UTF32BigEndian
        This.Index += 4
    ElseIf _
        This.CharacterData[0] = Poodle.UTF16LittleEndianMark(0) And _
        This.CharacterData[1] = Poodle.UTF16LittleEndianMark(1) And _
        This.CharacterData[2] = Poodle.UTF16LittleEndianMark(2) And _
        This.CharacterData[3] = Poodle.UTF16LittleEndianMark(3) Then
        This.ByteOrderData = Poodle.UTF32Stream.UTF32LittleEndian
        This.Index += 4
    Else
        This.ByteOrderData = Poodle.UTF32Stream.UTF32BigEndian
    End If
End Sub

Function Poodle.UTF32Stream.GetCharacter() As Poodle.Unicode.Codepoint
    If This.Status = CharacterStream.CharacterStreamInvalid Then
        Return Poodle.Unicode.InvalidCharacter
    End If
    
    If This.Index+3 >= This.Size Then
        This.Index = This.Size
        Return Poodle.Unicode.NullCharacter
    End If

    Dim Character As Unicode.Codepoint
    If This.ByteOrder = Poodle.UTF32Stream.UTF32BigEndian Then
        Character = _
            (Cast(Integer, This.CharacterData[This.Index]) Shl 24) Or _
            (Cast(Integer, This.CharacterData[This.Index+1]) Shl 16) Or _
            (Cast(Integer, This.CharacterData[This.Index+2]) Shl 8) Or _
            (Cast(Integer, This.CharacterData[This.Index+3]))
    Else
        Character = _
            (Cast(Integer, This.CharacterData[This.Index+3]) Shl 24) Or _
            (Cast(Integer, This.CharacterData[This.Index+2]) Shl 16) Or _
            (Cast(Integer, This.CharacterData[This.Index+1]) Shl 8) Or _
            (Cast(Integer, This.CharacterData[This.Index]))
    End If
    
    This.Index += 4
    Return Character
End Function
