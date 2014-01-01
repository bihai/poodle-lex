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

#include "Unicode.bi"
#include "UnicodeConstants.bi"

Constructor Poodle.UnicodeText()
    This.InternalData = 0
    This.Capacity = 0
    This.InternalLength = 0
End Constructor

Constructor Poodle.UnicodeText(ByRef Rhs As Poodle.UnicodeText)
    This.InternalData = Rhs.InternalData
    This.Capacity = Rhs.Capacity
    This.InternalLength = Rhs.InternalLength
    Rhs.InternalData = 0
    Rhs.Capacity = 0
    Rhs.InternalLength = 0
End Constructor

Operator Poodle.UnicodeText.Let(ByRef Rhs As Poodle.UnicodeText)
    This.InternalData = Rhs.InternalData
    This.Capacity = Rhs.Capacity
    This.InternalLength = Rhs.InternalLength
    Rhs.InternalData = 0
    Rhs.Capacity = 0
    Rhs.InternalLength = 0
End Operator    

Destructor Poodle.UnicodeText()
    If This.InternalData <> 0 Then
        Delete[] This.InternalData
    End If
End Destructor

Function Poodle.UnicodeText.Append(ByVal Character As UnicodeCodepoint) As Integer
    If Capacity = 0 Then
        This.InternalData = New UnicodeCodepoint[16]
        If This.InternalData = 0 Then Return 0
        This.Capacity = 16
    End If
    
    If This.InternalLength >= 1024 Then Return 0
    
    If This.InternalLength >= This.Capacity Then
        Var NewText = New UnicodeCodepoint[This.Capacity*2]
        If NewText = 0 Then Return 0
        For i As Integer = 0 To This.InternalLength - 1
            NewText[i] = This.InternalData[i]
        Next i
        Delete[] This.InternalData
        This.InternalData = NewText
        This.Capacity *= 2
    End If
    
    This.InternalData[This.InternalLength] = Character
    This.InternalLength += 1
    
    Return 1
End Function

Property Poodle.UnicodeText.Length() As Integer
    Return This.InternalLength
End Property

Property Poodle.UnicodeText.Data() As UnicodeCodepoint Pointer
    Return This.InternalData
End Property

Function Poodle.UnicodeText.ToUtf8String() As String
    Dim UTF8String As String
    For i As Integer = 0 To This.InternalLength - 1
        Var CodePoint = This.InternalData[i]
        Dim As Unsigned Byte Character(0 To 3)
        Select Case CodePoint
            Case 0 To &h7f
            UTF8String += Chr(Cast(Unsigned Byte, CodePoint))
            
            Case &h80 To &h7ff
            UTF8String += Chr(Poodle.UTF8HeadByteHeaderValue(2) Or Cast(Unsigned Byte, CodePoint Shr 6))
            UTF8String += Chr(Poodle.UTF8TailByteHeaderValue Or Cast(Unsigned Byte, ((CodePoint Shr 0) And Cast(Poodle.UnicodeCodePoint, Poodle.UTF8TailByteMask))))
            
            Case &h800 To &hffff
            UTF8String += Chr(Poodle.UTF8HeadByteHeaderValue(3) Or Cast(Unsigned Byte, CodePoint Shr 12))
            UTF8String += Chr(Poodle.UTF8TailByteHeaderValue Or Cast(Unsigned Byte, (CodePoint Shr 6) And Poodle.UTF8TailByteMask))
            UTF8String += Chr(Poodle.UTF8TailByteHeaderValue Or Cast(Unsigned Byte, (CodePoint Shr 0) And Poodle.UTF8TailByteMask))
            
            Case &h10000 To &h1fffff
            UTF8String += Chr(Poodle.UTF8HeadByteHeaderValue(4) Or Cast(Unsigned Byte, CodePoint Shr 18))
            UTF8String += Chr(Poodle.UTF8TailByteHeaderValue Or Cast(Unsigned Byte, (CodePoint Shr 12) And Poodle.UTF8TailByteMask))
            UTF8String += Chr(Poodle.UTF8TailByteHeaderValue Or Cast(Unsigned Byte, (CodePoint Shr 6) And Poodle.UTF8TailByteMask))
            UTF8String += Chr(Poodle.UTF8TailByteHeaderValue Or Cast(Unsigned Byte, (CodePoint Shr 0) And Poodle.UTF8TailByteMask))
        End Select
    Next i
    
    Return UTF8String
End Function
