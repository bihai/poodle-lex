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

#include "UnicodeConstants.bi"

Dim Shared Poodle.UTF8TailByteHeaderMask As Const Unsigned Byte = &b11000000
Dim Shared Poodle.UTF8TailByteHeaderValue As Const Unsigned Byte = &b10000000
Dim Shared Poodle.UTF8TailByteMask As Const Unsigned Byte = &b00111111

Dim Shared Poodle.UTF8HeadByteHeaderMask(1 To 4) As Const Unsigned Byte = {_
    &b10000000, _
    &b11100000, _
    &b11110000, _
    &b11111000 _
}

Dim Shared Poodle.UTF8HeadByteHeaderValue(1 To 4) As Const Unsigned Byte = { _
    &b00000000, _
    &b11000000, _
    &b11100000, _
    &b11110000 _
}

Dim Shared Poodle.UTF8HeadByteMask(1 To 4) As Const Unsigned Byte = { _
    &b01111111, _
    &b00011111, _
    &b00001111, _
    &b00000111 _
}

Dim Shared Poodle.UTF16SurrogateOffset As Const Integer = &h10000 - (&hD800 Shl 10) - &hDC00

Dim Shared Poodle.UTF16BigEndianMark(0 To 1) As Const Unsigned Byte = {&hFE, &hFF}
Dim Shared Poodle.UTF16LittleEndianMark(0 To 1) As Const Unsigned Byte = {&hFF, &hFE}

Dim Shared Poodle.UTF32BigEndianMark(0 To 3) As Const Unsigned Byte = {0, 0, &hFE, &hFF}
Dim Shared Poodle.UTF32LittleEndianMark(0 To 3) As Const Unsigned Byte = {&hFF, &hFE, 0, 0}
