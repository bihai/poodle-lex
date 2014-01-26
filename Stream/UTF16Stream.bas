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
#include "UTF16Stream.bi"
#include "UnicodeConstants.bi"

Constructor Poodle.Utf16Stream()
End Constructor

Constructor Poodle.UTF16Stream(Filename As String)
    Base(Filename)
    This.DetectByteOrder()
End Constructor

Constructor Poodle.UTF16Stream(CharacterData As Unsigned Byte Pointer, SizeInBytes As Unsigned LongInt)
    Base(CharacterData, SizeInBytes)
    This.DetectByteOrder()
End Constructor

Property Poodle.UTF16Stream.ByteOrder() As Poodle.UTF16Stream.ByteOrderType
    Return This.ByteOrderData
End Property

Property Poodle.UTF16Stream.ByteOrder(ByVal Order As Poodle.UTF16Stream.ByteOrderType)
    This.ByteOrderData = Order
End Property

Sub Poodle.UTF16Stream.DetectByteOrder()
    If This.Size < 2 Then 
        This.ByteOrderData = Poodle.UTF16Stream.UTF16BigEndian
    ElseIf _
        This.CharacterData[0] = Poodle.UTF16BigEndianMark(0) And _
        This.CharacterData[1] = Poodle.UTF16BigEndianMark(1) Then
        This.ByteOrderData = Poodle.UTF16Stream.UTF16BigEndian
        This.Index += 2
    ElseIf _
        This.CharacterData[0] = Poodle.UTF16LittleEndianMark(0) And _
        This.CharacterData[1] = Poodle.UTF16LittleEndianMark(1) Then
        This.ByteOrderData = Poodle.UTF16Stream.UTF16LittleEndian
        This.Index += 2
    Else
        This.ByteOrderData = Poodle.UTF16Stream.UTF16BigEndian
    End If
End Sub

Function Poodle.UTF16Stream.GetCharacter() As Poodle.Unicode.Codepoint
    If This.Status = CharacterStream.CharacterStreamInvalid Then
        Return Poodle.Unicode.InvalidCharacter
    End If
    
    If This.Index+1 >= This.Size Then
        Return Poodle.Unicode.NullCharacter
    End If

    Dim Lead As Unsigned Short
    Dim Trail As Unsigned Short
    If This.ByteOrder = UTF16BigEndian Then
        Lead = (Cast(Unsigned Short, This.CharacterData[This.Index]) Shl 8) + This.CharacterData[This.Index+1]
    Else
        Lead = (Cast(Unsigned Short, This.CharacterData[This.Index+1]) Shl 8) + This.CharacterData[This.Index]
    End If
    
    Select Case Lead
        Case &hD800 To &hDFFF
        If This.Index+3 >= This.Size Then
            This.Index += 4
            Return Poodle.Unicode.InvalidCharacter
        End If
        If This.ByteOrder = UTF16BigEndian Then
            Trail = (Cast(Unsigned Short, This.CharacterData[This.Index+2]) Shl 8) + This.CharacterData[This.Index+3]
        Else
            Trail = (Cast(Unsigned Short, This.CharacterData[This.Index+3]) Shl 8) + This.CharacterData[This.Index+2]
        End If
        This.Index += 4
        Return (Cast(Integer, Lead) Shl 10) + Cast(Integer, Trail) + Poodle.UTF16SurrogateOffset
        
        Case Else
        This.Index += 2
        Return Cast(Integer, Lead)
    End Select
    
End Function
