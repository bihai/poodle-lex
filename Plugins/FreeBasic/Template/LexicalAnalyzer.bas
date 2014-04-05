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

#include "$CLASS_NAME.bi"
#include "UnicodeConstants.bi"

Constructor Poodle.Token()
    This.Id = Poodle.Token.InvalidCharacter
End Constructor

Constructor Poodle.Token(ByVal Id As Poodle.Token.TokenId, ByVal Text As Poodle.Unicode.Text)
    This.Id = Id
    This.Text = Text
End Constructor

Function Poodle.Token.ToString(ByRef _Encoding As Poodle.Unicode.StringEncoding) As String
    Dim EncodedString As String
    Dim UnicodeString(1 To 3) As Poodle.Unicode.Text = { _
        Poodle.Unicode.Text("Token("), _
        Poodle.Unicode.Text(", '"), _
        Poodle.Unicode.Text("')") _
    }
    EncodedString += UnicodeString(1).ToString(_Encoding)
    EncodedString += This.GetIdAsString(_Encoding)
    EncodedString += UnicodeString(2).ToString(_Encoding)
    EncodedString += This.Text.ToString(_Encoding)
    EncodedString += UnicodeString(3).ToString(_Encoding)
    Return EncodedString
End Function

Function Poodle.Token.GetIdAsString(ByRef _Encoding As Poodle.Unicode.StringEncoding) As String
    Var Text = Poodle.Unicode.Text(*Poodle.Token.IdNames(This.Id))
    Return Text.ToString(_Encoding)
End Function

Dim Poodle.Token.IdNames(0 To $TOKEN_IDNAMES_LIMIT) As Const ZString Pointer = { _
    @"InvalidCharacter", _
    @"EndOfStream", _
    $TOKEN_IDNAMES
}

Constructor Poodle.$CLASS_NAME(Stream As CharacterStream Pointer)
    This.Stream = Stream
    This.Character = Stream->GetCharacter()
End Constructor

Function Poodle.$CLASS_NAME.IsEndOfStream() As Integer
    Return This.Stream->IsEndOfStream()
End Function

Namespace Poodle
    Enum ${CLASS_NAME}State
        $ENUM_STATE_IDS
    End Enum
End Namespace

Function Poodle.$CLASS_NAME.GetToken() As Poodle.Token
    Dim State As Poodle.${CLASS_NAME}State = Poodle.$INITIAL_STATE
    Dim Text As Poodle.Unicode.Text
    Do
        Dim Capture As Integer = 0
        Select Case State:
            $STATE_MACHINE
        End Select
        If Capture = 1 Then Text.Append(This.Character)
        This.Character = This.Stream->GetCharacter()
    Loop
End Function

