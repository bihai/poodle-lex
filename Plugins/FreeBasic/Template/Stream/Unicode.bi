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

#ifndef POODLE_UNICODE_BI
#define POODLE_UNICODE_BI

Namespace Poodle
    Namespace Unicode
        Type Codepoint As Integer
        Extern InvalidCharacter As Const Codepoint
        Extern NullCharacter As Const Codepoint
        
        Type StringEncoding Extends Object
            Declare Abstract Function Decode(ByRef As Const String, ByRef As Integer) As Codepoint
            Declare Abstract Sub Encode(ByRef As String, ByVal As Codepoint)
        End Type
        
        Extern DefaultStringEncoding As StringEncoding Pointer ' UTF8
        
        Enum TextState
            TextStateValid
            TextStateInvalid
        End Enum
        
        Type Text Extends Object
            Public:
            Declare Constructor()
            Declare Constructor(ByRef Rhs As Text)
            Declare Constructor(ByRef Rhs As Const Text)
            Declare Constructor(ByRef As Const String, ByRef As StringEncoding = *DefaultStringEncoding)
            Declare Operator Let(ByRef Rhs As Text)
            Declare Operator Let(ByRef Rhs As Const Text)
            Declare Property Length As Integer
            Declare Property Data As Codepoint Pointer
            Declare Function Append(ByVal Character As Codepoint) As Integer
            Declare Function ToString(ByRef As StringEncoding = *DefaultStringEncoding) As String
            Declare Destructor()
            
            Private:
            InternalData As Codepoint Pointer
            Capacity As Integer
            InternalLength As Integer
            State As TextState
        End Type
    End Namespace
End Namespace

#endif
