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

#include "$BASE_FILE_NAME.bi"
#include "UnicodeConstants.bi"

Constructor $NAMESPACE.${CLASS_NAME}Token()
    This.Id = $NAMESPACE.${CLASS_NAME}Token.InvalidCharacter
End Constructor

Constructor $NAMESPACE.${CLASS_NAME}Token(ByVal Id As $NAMESPACE.${CLASS_NAME}Token.TokenId, ByVal Text As Poodle.Unicode.Text)
    This.Id = Id
    This.Text = Text
End Constructor

Function $NAMESPACE.${CLASS_NAME}Token.ToString(ByRef _Encoding As Poodle.Unicode.StringEncoding) As String
    Dim EncodedString As String
    Dim UnicodeString(1 To 4) As Poodle.Unicode.Text = { _
        Poodle.Unicode.Text("Token("), _
        Poodle.Unicode.Text(", '"), _
        Poodle.Unicode.Text("')"), _
        Poodle.Unicode.Text(")") _
    }
    EncodedString += UnicodeString(1).ToString(_Encoding)
    EncodedString += This.GetIdAsString(_Encoding)
    If This.Text.Length > 0 Then
        EncodedString += UnicodeString(2).ToString(_Encoding)
        EncodedString += This.Text.ToString(_Encoding)
        EncodedString += UnicodeString(3).ToString(_Encoding)
    Else
        EncodedString += UnicodeString(4).ToString(_Encoding)
    End If
    Return EncodedString
End Function

Function $NAMESPACE.${CLASS_NAME}Token.GetIdAsString(ByRef _Encoding As Poodle.Unicode.StringEncoding) As String
    Var Text = Poodle.Unicode.Text(*$NAMESPACE.${CLASS_NAME}Token.IdNames(This.Id))
    Return Text.ToString(_Encoding)
End Function

Dim $NAMESPACE.${CLASS_NAME}Token.IdNames(0 To $TOKEN_IDNAMES_LIMIT) As Const ZString Pointer = { _
    @"InvalidToken", _
    @"EndOfStream", _
    $TOKEN_IDNAMES
}

Constructor $NAMESPACE.$CLASS_NAME(Stream As Poodle.CharacterStream Pointer)
    This.Stream = Stream
    This.Character = Stream->GetCharacter()
End Constructor

Function $NAMESPACE.$CLASS_NAME.IsEndOfStream() As Integer
    Return This.Stream->IsEndOfStream()
End Function

Namespace $NAMESPACE
    Enum ${CLASS_NAME}State
        $ENUM_STATE_IDS
    End Enum
End Namespace

Function $NAMESPACE.$CLASS_NAME.GetToken() As $NAMESPACE.${CLASS_NAME}Token
    Dim State As $NAMESPACE.${CLASS_NAME}State = $NAMESPACE.$INITIAL_STATE
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
