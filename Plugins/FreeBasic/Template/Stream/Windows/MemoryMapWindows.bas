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

#include "windows.bi"
#include "MemoryMapWindows.bi"

Function Poodle.MemoryMap.Open(Filename As String) As MemoryMap Pointer
    Var MemoryMapObject = New Poodle.MemoryMapWindows(Filename)
    Return Cast(MemoryMap Pointer, MemoryMapObject)    
End Function

Constructor Poodle.MemoryMapWindows(Filename As String)
    This.Status = Poodle.MemoryMap.MemoryMapInvalid
    
    Dim FileInfo As WIN32_FILE_ATTRIBUTE_DATA 
    If GetFileAttributesEx(Filename, GetFileExInfoStandard, @FileInfo) = 0 Then
        This.FileMappingHandle = 0
        This.FileData = 0
        Exit Constructor
    End If
    This.Size = Cast(Unsigned LongInt, FileInfo.nFileSizeHigh) Shl 32
    This.Size Or= Cast(Unsigned LongInt, FileInfo.nFileSizeLow)
    
    This.FileHandle = CreateFile( _
        @Filename[0], _
        GENERIC_READ, _
        FILE_SHARE_READ, _
        NULL, _
        OPEN_EXISTING, _
        FILE_ATTRIBUTE_NORMAL, _
        NULL _
    )
    If This.FileHandle = 0 Then
        This.Status = Poodle.MemoryMap.MemoryMapInvalid
        This.FileMappingHandle = 0
        This.FileData = 0
        Exit Constructor
    End If
    
    This.FileMappingHandle = CreateFileMapping(This.FileHandle, NULL, PAGE_READONLY, 0, 0, NULL)
    If This.FileMappingHandle = 0 Then
        This.Status = Poodle.MemoryMap.MemoryMapInvalid
        This.FileData = 0
        Exit Constructor
    End If
    
    This.FileData = MapViewOfFile(This.FileMappingHandle, FILE_MAP_READ, 0, 0, 0)
    If This.FileData = NULL Then
        This.Status = Poodle.MemoryMap.MemoryMapInvalid
        Exit Constructor
    End If    
    
    This.Status = Poodle.MemoryMap.MemoryMapValid
End Constructor

Function Poodle.MemoryMapWindows.GetData() As Unsigned Byte Pointer
    Return Cast(Unsigned Byte Pointer, This.FileData)
End Function

Function Poodle.MemoryMapWindows.GetSize() As Unsigned LongInt
    Return This.Size
End Function

Function Poodle.MemoryMapWindows.GetStatus() As Poodle.MemoryMap.MemoryMapStatus
    Return This.Status
End Function

Destructor Poodle.MemoryMapWindows()
    If This.FileMappingHandle <> 0 Then
        CloseHandle(This.FileMappingHandle)
        This.FileMappingHandle = 0
        This.FileData = 0
    End If
    If This.FileHandle <> 0 Then
        CloseHandle(This.FileHandle)
        This.FileHandle = 0
    End If
End Destructor
