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

#ifndef POODLE_MEMORYMAP_WINDOWS
#define POODLE_MEMORYMAP_WINDOWS

#include "MemoryMap.bi"
#include "windows.bi"

Namespace Poodle
    Type MemoryMapWindows Extends MemoryMap
        Public:
        Declare Constructor(Filename As String)
        Declare Virtual Function GetStatus() As MemoryMap.MemoryMapStatus
        Declare Virtual Function GetData() As Unsigned Byte Pointer
        Declare Virtual Function GetSize() As Unsigned LongInt
        Declare Virtual Destructor()
        
        Private:
        FileHandle As HANDLE
        FileMappingHandle As HANDLE
        FileData As LPVOID
        Size As Unsigned LongInt
        Status As MemoryMap.MemoryMapStatus
    End Type
End Namespace

#endif
