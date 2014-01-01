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

#include "LexicalAnalyzer.bi"
#include "UnicodeConstants.bi"

Constructor Poodle.Token()
    This.Id = Poodle.Token.InvalidCharacter
End Constructor

Constructor Poodle.Token(ByVal Id As Poodle.Token.TokenId, ByVal Text As Poodle.UnicodeText)
    This.Id = Id
    This.Text = Text
End Constructor

Constructor Poodle.LexicalAnalyzer(Stream As CharacterStream Ptr)
    This.Stream = Stream
    This.Character = Stream->GetCharacter()
End Constructor

Function Poodle.LexicalAnalyzer.IsEndOfStream() As Integer
    Return This.Stream->IsEndOfStream()
End Function

Namespace Poodle
    Enum LexicalAnalyzerState
        $ENUM_STATE_IDS
    End Enum
End Namespace

Function Poodle.LexicalAnalyzer.GetToken() As Poodle.Token
    Dim State As Poodle.LexicalAnalyzerState = Poodle.$INITIAL_STATE
    Dim Text As Poodle.UnicodeText
    Do
        If This.Stream->IsEndOfStream() Then
            Return Poodle.Token(Poodle.Token.EndOfStream, UnicodeText())
        End If
        Select Case State:
            $STATE_MACHINE
        End Select
        Text.Append(This.Character)
        This.Character = This.Stream->GetCharacter()
    Loop
End Function
