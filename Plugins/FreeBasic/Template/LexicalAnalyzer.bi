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

#ifndef POODLE_LEXICALANALYZER_BI
#define POODLE_LEXICALANALYZER_BI

#include "Stream\Unicode.bi"
#include "Stream\CharacterStream.bi"

Namespace Poodle
    Type Token
        Public:
        Enum TokenId
            InvalidCharacter
            EndOfStream
            $ENUM_TOKEN_IDS
        End Enum
        Id As TokenId
        Text As Unicode.Text
        
        
        Declare Constructor()
        Declare Constructor(ByVal Id As TokenId, ByVal Text As Unicode.Text)
        Declare Function ToString(ByRef _Encoding As Unicode.StringEncoding = *Unicode.DefaultStringEncoding) As String
        Declare Function GetIdAsString(ByRef _Encoding As Unicode.StringEncoding = *Unicode.DefaultStringEncoding) As String
        
        Private:
        Static IdNames(0 To $TOKEN_IDNAMES_LIMIT) As Const ZString Pointer 
    End Type

    Type LexicalAnalyzer Extends Object
        Public:
        Declare Constructor(Stream As CharacterStream Ptr)
        Declare Function IsEndOfStream() As Integer
        Declare Function GetToken() As Token
        
        Private:
        Stream As CharacterStream Ptr
        Character As Unicode.CodePoint
    End Type

End Namespace
    
#endif
