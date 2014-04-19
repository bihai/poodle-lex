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

Dim Shared Poodle.Unicode.InvalidCharacter As Const Integer = &hFFFF
Dim Shared Poodle.Unicode.NullCharacter As Const Integer = &h0000

Constructor Poodle.Unicode.Text()
    This.InternalData = 0
    This.Capacity = 0
    This.InternalLength = 0
End Constructor

Constructor Poodle.Unicode.Text(ByRef Value As Const String, ByRef _Encoding As Poodle.Unicode.StringEncoding)
    Dim Index As Integer = 0
    While Index < Len(Value)
        This.Append(_Encoding.Decode(Value, Index))
    Wend
End Constructor

Constructor Poodle.Unicode.Text(ByRef Rhs As Poodle.Unicode.Text)
    This.State = Poodle.Unicode.TextStateValid
    This.InternalData = Rhs.InternalData
    This.Capacity = Rhs.Capacity
    This.InternalLength = Rhs.InternalLength
    Rhs.InternalData = 0
    Rhs.Capacity = 0
    Rhs.InternalLength = 0
End Constructor

Constructor Poodle.Unicode.Text(ByRef Rhs As Const Poodle.Unicode.Text)
    This.State = Poodle.Unicode.TextStateValid
    This.InternalData = New Poodle.Unicode.Codepoint[Rhs.Capacity]
    If This.InternalData = 0 Then
        This.State = Poodle.Unicode.TextStateInvalid
        Return
    End If
    
    For i As Integer = 0 To Rhs.InternalLength-1
        This.InternalData[i] = Rhs.InternalData[i]
    Next i
    This.Capacity = Rhs.Capacity
    This.InternalLength = Rhs.InternalLength
End Constructor

Operator Poodle.Unicode.Text.Let(ByRef Rhs As Poodle.Unicode.Text)
    This.InternalData = Rhs.InternalData
    This.Capacity = Rhs.Capacity
    This.InternalLength = Rhs.InternalLength
    Rhs.InternalData = 0
    Rhs.Capacity = 0
    Rhs.InternalLength = 0
End Operator    

Operator Poodle.Unicode.Text.Let(ByRef Rhs As Const Poodle.Unicode.Text)
    This.State = Poodle.Unicode.TextStateValid
    This.InternalData = New Poodle.Unicode.Codepoint[Rhs.Capacity]
    If This.InternalData = 0 Then
        This.State = Poodle.Unicode.TextStateInvalid
        Return
    End If
    For i As Integer = 0 To Rhs.InternalLength-1
        This.InternalData[i] = Rhs.InternalData[i]
    Next i
    This.Capacity = Rhs.Capacity
    This.InternalLength = Rhs.InternalLength
End Operator

Destructor Poodle.Unicode.Text()
    If This.InternalData <> 0 Then
        Delete[] This.InternalData
    End If
End Destructor

Function Poodle.Unicode.Text.Append(ByVal Character As Unicode.Codepoint) As Integer
    If Capacity = 0 Then
        This.InternalData = New Poodle.Unicode.Codepoint[16]
        If This.InternalData = 0 Then Return 0
        This.Capacity = 16
    End If
    
    If This.InternalLength >= This.Capacity Then
        Var NewText = New Poodle.Unicode.Codepoint[This.Capacity*2]
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

Property Poodle.Unicode.Text.Length() As Integer
    Return This.InternalLength
End Property

Property Poodle.Unicode.Text.Data() As Poodle.Unicode.Codepoint Pointer
    Return This.InternalData
End Property

Function Poodle.Unicode.Text.ToString(ByRef _Encoding As Poodle.Unicode.StringEncoding) As String
    Dim EncodedString As String = ""
    For i As Integer = 0 To This.InternalLength-1
        _Encoding.Encode(EncodedString, This.InternalData[i])
    Next i
    Return EncodedString
End Function
