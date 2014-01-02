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

#include "UTF8Stream.bi"
#include "LexicalAnalyzer.bi"

Dim As Poodle.Token.TokenID ExpectedTokens(0 to 6) = { _
    Poodle.Token.Float, _
    Poodle.Token.Keyword, _
    Poodle.Token.Whitespace, _
    Poodle.Token.Integer_, _
    Poodle.Token.Identifier, _
    Poodle.Token.Newline, _
    Poodle.Token.EndOfStream _
}

Dim As String ExpectedTexts(0 to 6) = { _
    "123.45", _
    "K€yword", _
    "    ", _
    "12345", _
    "Hello", _
    Chr(13) + Chr(10), _
    "" _
}

Var InputFile = Poodle.UTF8Stream("Test.txt")
If InputFile.GetStatus() = Poodle.CharacterStream.CharacterStreamInvalid Then
    Print "Could not open test file"
    End
End If

Var LexicalAnalyzer = Poodle.LexicalAnalyzer(@InputFile)
Dim As Integer FoundMismatch = 0
For i As Integer = 0 To 6
    Var Token = LexicalAnalyzer.GetToken()
    If ExpectedTokens(i) <> Token.Id Then
        Print "Token mismatch: expected "; Str(ExpectedTokens(i)); ", found "; Token.id
        FoundMismatch = 1
    End If
    If ExpectedTexts(i) <> Token.Text.ToUtf8String() Then
        Print "Text mismatch: expected '"; ExpectedTexts(i); "', found '"; Token.Text.ToUtf8String(); "'"
        FoundMismatch = 1
    End If
Next i

If FoundMismatch <> 0 Then
    Print
    Print "...Found errors"
Else
    Print "Completed successfully"
End If
