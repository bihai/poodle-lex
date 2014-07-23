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

#include "vbcompat.bi"
#include "UTF8Stream.bi"
#include "$BASE_FILE_NAME.bi"

If Len(Command(1)) = 0 Then
    Print "usage: Demo [input_file_to_scan]"
    End
End If

If FileExists(Command(1)) = 0 Then
    Print "Could not find input file '"; Command(1); "'"
    End
End If

Var InputFile = Poodle.UTF8Stream(Command(1))

If InputFile.GetStatus() = Poodle.CharacterStream.CharacterStreamInvalid Then
    Print "Could not open input file '"; Command(1); "'"
    End
End If

Var LexicalAnalyzer = $NAMESPACE.$CLASS_NAME(@InputFile)
Var Token = LexicalAnalyzer.GetToken()
Do While Token.Id <> $NAMESPACE.LexicalAnalyzerToken.EndOfStream
    Print Token.ToString()
    Token = LexicalAnalyzer.GetToken()
Loop
