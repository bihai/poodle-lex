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

#ifndef $HEADER_GUARD_MODE_NAME
#define $HEADER_GUARD_MODE_NAME

#define $STACK_DEPTH_ID $STACK_DEPTH

Namespace $NAMESPACE
    Type $MODE_STACK_CLASS_NAME
        Protected:
        Enum ModeId
            $ENUM_MODE_IDS
        End Enum
        Declare Constructor()
        Declare Property Mode() As ModeId
        Declare Sub EnterSection(ByVal As ModeId)
        Declare Sub ExitSection()
        Declare Sub SwitchSection(ByVal As ModeId)
        Declare Sub Reset()
        
        Private:
        Dim Stack(1 To $STACK_DEPTH_ID) As ModeId
        Dim Index As Integer
    End Type
End Namespace

#endif