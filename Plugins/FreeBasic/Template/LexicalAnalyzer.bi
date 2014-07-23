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
$MODE_INCLUDE

Namespace $NAMESPACE
    Type ${TYPE_REL_TOKEN}
        Public:
        Enum TokenId
            InvalidCharacter
            EndOfStream
            $ENUM_TOKEN_IDS
        End Enum

        Id As TokenId
        Text As ${TYPE_REL_TEXT}
        
        Declare Constructor()
        Declare Constructor(ByVal Id As TokenId, ByVal Text As ${TYPE_REL_TEXT})
        Declare Function ToString(ByRef _Encoding As ${TYPE_REL_ENCODING} = *${DEFAULT_ENCODING}) As String
        Declare Function GetIdAsString(ByRef _Encoding As ${TYPE_REL_ENCODING} = *${DEFAULT_ENCODING}) As String
        
        Private:
        Static IdNames(0 To $TOKEN_IDNAMES_LIMIT) As Const ZString Pointer 
    End Type
    
    Type $CLASS_NAME Extends $BASE_CLASS
        Public:
        Declare Constructor(Stream As ${TYPE_REL_STREAM} Ptr)
        Declare Function IsEndOfStream() As Integer
        Declare Function GetToken() As ${TYPE_REL_TOKEN}
        
        Private:
        $STATE_MACHINE_DECLARATIONS
        Stream As ${TYPE_REL_STREAM} Ptr
        Character As ${TYPE_REL_CHARACTER}
    End Type

End Namespace
    
#endif
