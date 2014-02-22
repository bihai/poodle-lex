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

#ifndef POODLE_MEMORYMAP_BI
#define POODLE_MEMORYMAP_BI

Namespace Poodle
    
    '' Simple portable memory-map interface 
    Type MemoryMap Extends Object
        Public:
        Enum MemoryMapStatus
            MemoryMapInvalid
            MemoryMapValid
        End Enum
        
        Declare Static Function Open(Filename As String) As MemoryMap Pointer
        Declare Abstract Function GetStatus() As MemoryMapStatus
        Declare Abstract Function GetData() As Unsigned Byte Pointer
        Declare Abstract Function GetSize() As Unsigned LongInt
        Declare Virtual Destructor()
    End Type
    
End Namespace

#endif
