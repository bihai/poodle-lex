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

#ifndef $HEADER_GUARD_NAME
#define $HEADER_GUARD_NAME

#include "Stream\Unicode.bi"
#include "Stream\CharacterStream.bi"

Namespace $NAMESPACE
    Type ${CLASS_NAME}Token
        Public:
        Enum TokenId
            InvalidCharacter
            EndOfStream
            $ENUM_TOKEN_IDS
        End Enum
        Id As TokenId
        Text As ${RELATIVE_NAMESPACE}Unicode.Text
        
        Declare Constructor()
        Declare Constructor(ByVal Id As TokenId, ByVal Text As ${RELATIVE_NAMESPACE}Unicode.Text)
        Declare Function ToString(ByRef _Encoding As ${RELATIVE_NAMESPACE}Unicode.StringEncoding = *${RELATIVE_NAMESPACE}Unicode.DefaultStringEncoding) As String
        Declare Function GetIdAsString(ByRef _Encoding As ${RELATIVE_NAMESPACE}Unicode.StringEncoding = *${RELATIVE_NAMESPACE}Unicode.DefaultStringEncoding) As String
        
        Private:
        Static IdNames(0 To $TOKEN_IDNAMES_LIMIT) As Const ZString Pointer 
    End Type

    Type $CLASS_NAME Extends Object
        Public:
        Declare Constructor(Stream As ${RELATIVE_NAMESPACE}CharacterStream Ptr)
        Declare Function IsEndOfStream() As Integer
        Declare Function GetToken() As ${CLASS_NAME}Token
        
        Private:
        Stream As ${RELATIVE_NAMESPACE}CharacterStream Ptr
        Character As ${RELATIVE_NAMESPACE}Unicode.CodePoint
    End Type

End Namespace
    
#endif
