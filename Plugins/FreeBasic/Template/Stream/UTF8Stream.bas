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
#include "UTF8Stream.bi"
#include "UnicodeConstants.bi"

Dim Shared UTF8EncodingObject As Poodle.UTF8StringEncoding
Dim Shared Poodle.Unicode.DefaultStringEncoding As Poodle.Unicode.StringEncoding Pointer = @UTF8EncodingObject

Constructor Poodle.UTF8Stream()
End Constructor

Constructor Poodle.UTF8Stream(Filename As String)
    Base(Filename)
End Constructor

Constructor Poodle.UTF8Stream(CharacterData As Unsigned Byte Pointer, SizeInBytes As Unsigned LongInt)
    Base(CharacterData, SizeInBytes)
End Constructor

Function GetUTF8CharacterLengthInBytes(ByVal Header As Unsigned Byte) As Integer Static
    For i As Integer = 1 To 4
        If (Header And Poodle.UTF8HeadByteHeaderMask(i)) = Poodle.UTF8HeadByteHeaderValue(i) Then
            Return i
        End If
    Next i
    Return 0
End Function

Function Poodle.UTF8Stream.GetCharacter() As Poodle.Unicode.Codepoint
    If This.Status = CharacterStream.CharacterStreamInvalid Then
        Return Poodle.Unicode.InvalidCharacter
    End If
    
    If This.Index >= This.Size Then
        Return Poodle.Unicode.NullCharacter
    End If

    Dim CharacterLengthInBytes As Unsigned LongInt = GetUTF8CharacterLengthInBytes(CharacterData[This.Index])
    Dim Character As Poodle.Unicode.Codepoint
    Select Case CharacterLengthInBytes
        Case 1
        Character = Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index])
        This.Index += 1
        
        Case 2
        If This.Index + 1 >= This.Size OrElse _
            (This.CharacterData[This.Index+1] And Poodle.UTF8TailByteHeaderMask) <> Poodle.UTF8TailByteHeaderValue Then
            Character = Poodle.Unicode.InvalidCharacter
        Else
            Character = _
                (Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index] And Poodle.UTF8HeadByteMask(2)) Shl 6) Or _
                (Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index+1] And Poodle.UTF8TailByteMask))
        End If
        This.Index += 2
        
        Case 3
        If This.Index + 2 >= This.Size OrElse _
            (This.CharacterData[This.Index+1] And Poodle.UTF8TailByteHeaderMask) <> Poodle.UTF8TailByteHeaderValue OrElse _
            (This.CharacterData[This.Index+2] And Poodle.UTF8TailByteHeaderMask) <> Poodle.UTF8TailByteHeaderValue Then
            Character = Poodle.Unicode.InvalidCharacter
        Else
            Character = _
                (Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index] And Poodle.UTF8HeadByteMask(3)) Shl 12) Or _
                (Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index+1] And Poodle.UTF8TailByteMask) Shl 6) Or _
                (Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index+2] And Poodle.UTF8TailByteMask))
        End If
        This.Index += 3
        
        Case 4
        If This.Index + 3 >= This.Size OrElse _
            (This.CharacterData[This.Index+1] And Poodle.UTF8TailByteHeaderMask) <> Poodle.UTF8TailByteHeaderValue OrElse _
            (This.CharacterData[This.Index+2] And Poodle.UTF8TailByteHeaderMask) <> Poodle.UTF8TailByteHeaderValue OrElse _
            (This.CharacterData[This.Index+3] And Poodle.UTF8TailByteHeaderMask) <> Poodle.UTF8TailByteHeaderValue Then
            Character = Poodle.Unicode.InvalidCharacter
        Else
            Character = _
                (Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index] And Poodle.UTF8HeadByteMask(4)) Shl 18) Or _
                (Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index+1] And Poodle.UTF8TailByteMask) Shl 12) Or _
                (Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index+2] And Poodle.UTF8TailByteMask) Shl 6) Or _
                (Cast(Poodle.Unicode.Codepoint, This.CharacterData[This.Index+3] And Poodle.UTF8TailByteMask))
        End If
        This.Index += 4
        
        Case Else
        Character = Poodle.Unicode.InvalidCharacter
        This.Index += 1
    End Select
    
    Return Character
End Function

Function Poodle.UTF8StringEncoding.Decode(ByRef Value As Const String, ByRef Index As Integer) As Poodle.Unicode.Codepoint
    If Len(Value) = 0 Then
        Return Poodle.Unicode.InvalidCharacter
        Index = 1
    End If
    
    Var Stream = UTF8Stream(Cast(Unsigned Byte Pointer, @Value[0]) + Index, Len(Value)-Index)
    Var Codepoint = Stream.GetCharacter()
    Select Case Codepoint
        Case &h80 To &h7ff
        Index += 2
        
        Case &h800 To &hfffe
        Index += 3
        
        Case &h10000 To &h1fffff
        Index += 4

        Case Else
        Index += 1
    End Select
    Return Codepoint
End Function

Function Poodle.UTF8StringEncoding.GetByteLength(ByVal Character As Poodle.Unicode.Codepoint) As Integer
    Select Case Character
        Case 0 To &h7f
        Return 1
       
        Case &h80 To &h7ff
        Return 2
        
        Case &h800 To &hffff
        Return 3
        
        Case &h10000 To &h1fffff
        Return 4
   
        Case Else
        Return 3
    End Select
End Function

Function Poodle.UTF8StringEncoding.Encode(ByVal Character As Unicode.CodePoint, ByVal Bytes As Unsigned Byte Pointer) As Integer
    Select Case Character
        Case 0 To &h7f
        *Bytes = Cast(Unsigned Byte, Character)
        Return 1
        
        Case &h80 To &h7ff
        *Bytes = Cast(Unsigned Byte, Character Shr 6) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8HeadByteHeaderValue(2))
        Bytes += 1
        *Bytes = Cast(Unsigned Byte, (Character Shr 0) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8TailByteMask))
        Return 2
        
        Case &h800 To &hffff
        *Bytes = Cast(Unsigned Byte, Character Shr 12) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8HeadByteHeaderValue(3))
        Bytes += 1
        *Bytes = Cast(Unsigned Byte, (Character Shr 6) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8TailByteMask))
        Bytes += 1
        *Bytes = Cast(Unsigned Byte, (Character Shr 0) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8TailByteMask))
        Return 3
        
        Case &h10000 To &h1fffff
        *Bytes = Cast(Unsigned Byte, Character Shr 18) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8HeadByteHeaderValue(4))
        Bytes += 1
        *Bytes = Cast(Unsigned Byte, (Character Shr 12) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8TailByteMask))
        Bytes += 1
        *Bytes = Cast(Unsigned Byte, (Character Shr 6) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8TailByteMask))
        Bytes += 1
        *Bytes = Cast(Unsigned Byte, (Character Shr 0) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8TailByteMask))
        Return 4
        
        Case Else
        *Bytes = Cast(Unsigned Byte, Unicode.InvalidCharacter Shr 12) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8HeadByteHeaderValue(3))
        Bytes += 1
        *Bytes = Cast(Unsigned Byte, (Unicode.InvalidCharacter Shr 6) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8TailByteMask))
        Bytes += 1
        *Bytes = Cast(Unsigned Byte, (Unicode.InvalidCharacter Shr 0) And Cast(Poodle.Unicode.Codepoint, Poodle.UTF8TailByteMask))
        Return 3
    End Select
End Function
