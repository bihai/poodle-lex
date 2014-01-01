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
    Type UnicodeCodepoint As Integer

    Type UnicodeText
        Public:
        Declare Constructor()
        Declare Constructor(ByRef Rhs As UnicodeText)
        Declare Operator Let(ByRef Rhs As UnicodeText)
        Declare Property Length As Integer
        Declare Property Data As UnicodeCodepoint Pointer
        Declare Function Append(ByVal Character As UnicodeCodepoint) As Integer
        Declare Function ToUTF8String As String
        Declare Destructor()
        
        Private:
        InternalData As UnicodeCodepoint Pointer
        Capacity As Integer
        InternalLength As Integer
    End Type
End Namespace

#endif
