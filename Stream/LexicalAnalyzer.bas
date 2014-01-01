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
        Float
        Float1
        FloatInteger_
        Identifier
        IdentifierKeyword
        IdentifierKeyword1
        IdentifierKeyword2
        IdentifierKeyword3
        IdentifierKeyword4
        IdentifierKeyword5
        IdentifierKeyword6
        InitialState
        Newline
        Newline1
        Whitespace
    End Enum
End Namespace

Function Poodle.LexicalAnalyzer.GetToken() As Poodle.Token
    Dim State As Poodle.LexicalAnalyzerState = Poodle.InitialState
    Dim Text As Poodle.UnicodeText
    Do
        If This.Stream->IsEndOfStream() Then
            Return Poodle.Token(Poodle.Token.EndOfStream, UnicodeText())
        End If
        Select Case State:
            Case Poodle.InitialState
            Select Case This.Character
                Case 13
                State = Poodle.Newline1
                
                Case 46
                State = Poodle.Float
                
                Case 48 To 57
                State = Poodle.FloatInteger_
                
                Case 65 To 90, 97 To 106, 108 To 122
                State = Poodle.Identifier
                
                Case 107
                State = Poodle.IdentifierKeyword
                
                Case 9, 32
                State = Poodle.Whitespace
                
                Case 10
                State = Poodle.Newline
                
                Case Else
                Text.Append(This.Character)
                This.Character = This.Stream->GetCharacter()
                Return Poodle.Token(Poodle.Token.InvalidCharacter, Text)
            End Select
            
            Case Poodle.Whitespace
            Select Case This.Character
                Case 9, 32
                State = Poodle.Whitespace
                
                Case Else
                Return Poodle.Token(Poodle.Token.Whitespace, Text)
            End Select
            
            Case Poodle.Newline
            Select Case This.Character
                Case Else
                Return Poodle.Token(Poodle.Token.Newline, Text)
            End Select
            
            Case Poodle.Newline1
            Select Case This.Character
                Case 10
                State = Poodle.Newline
                
                Case Else
                Return Poodle.Token(Poodle.Token.Newline, Text)
            End Select
            
            Case Poodle.Float
            Select Case This.Character
                Case 48 To 57
                State = Poodle.Float1
                
                Case Else
                Text.Append(This.Character)
                This.Character = This.Stream->GetCharacter()
                Return Poodle.Token(Poodle.Token.InvalidCharacter, Text)
            End Select
            
            Case Poodle.FloatInteger_
            Select Case This.Character
                Case 46
                State = Poodle.Float1
                
                Case 48 To 57
                State = Poodle.FloatInteger_
                
                Case Else
                Return Poodle.Token(Poodle.Token.Integer_, Text)
            End Select
            
            Case Poodle.Identifier
            Select Case This.Character
                Case 48 To 57, 65 To 90, 95, 97 To 122
                State = Poodle.Identifier
                
                Case Else
                Return Poodle.Token(Poodle.Token.Identifier, Text)
            End Select
            
            Case Poodle.IdentifierKeyword
            Select Case This.Character
                Case 101
                State = Poodle.IdentifierKeyword1
                
                Case 48 To 57, 65 To 90, 95, 97 To 100, 102 To 122
                State = Poodle.Identifier
                
                Case Else
                Return Poodle.Token(Poodle.Token.Identifier, Text)
            End Select
            
            Case Poodle.Float1
            Select Case This.Character
                Case 48 To 57
                State = Poodle.Float1
                
                Case Else
                Return Poodle.Token(Poodle.Token.Float, Text)
            End Select
            
            Case Poodle.IdentifierKeyword1
            Select Case This.Character
                Case 121
                State = Poodle.IdentifierKeyword2
                
                Case 48 To 57, 65 To 90, 95, 97 To 120, 122
                State = Poodle.Identifier
                
                Case Else
                Return Poodle.Token(Poodle.Token.Identifier, Text)
            End Select
            
            Case Poodle.IdentifierKeyword2
            Select Case This.Character
                Case 119
                State = Poodle.IdentifierKeyword3
                
                Case 48 To 57, 65 To 90, 95, 97 To 118, 120 To 122
                State = Poodle.Identifier
                
                Case Else
                Return Poodle.Token(Poodle.Token.Identifier, Text)
            End Select
            
            Case Poodle.IdentifierKeyword3
            Select Case This.Character
                Case 111
                State = Poodle.IdentifierKeyword4
                
                Case 48 To 57, 65 To 90, 95, 97 To 110, 112 To 122
                State = Poodle.Identifier
                
                Case Else
                Return Poodle.Token(Poodle.Token.Identifier, Text)
            End Select
            
            Case Poodle.IdentifierKeyword4
            Select Case This.Character
                Case 114
                State = Poodle.IdentifierKeyword5
                
                Case 48 To 57, 65 To 90, 95, 97 To 113, 115 To 122
                State = Poodle.Identifier
                
                Case Else
                Return Poodle.Token(Poodle.Token.Identifier, Text)
            End Select
            
            Case Poodle.IdentifierKeyword5
            Select Case This.Character
                Case 100
                State = Poodle.IdentifierKeyword6
                
                Case 48 To 57, 65 To 90, 95, 97 To 99, 101 To 122
                State = Poodle.Identifier
                
                Case Else
                Return Poodle.Token(Poodle.Token.Identifier, Text)
            End Select
            
            Case Poodle.IdentifierKeyword6
            Select Case This.Character
                Case 48 To 57, 65 To 90, 95, 97 To 122
                State = Poodle.Identifier
                
                Case Else
                Return Poodle.Token(Poodle.Token.Keyword, Text)
            End Select
        End Select
        Text.Append(This.Character)
        This.Character = This.Stream->GetCharacter()
    Loop
End Function
