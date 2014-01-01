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

#include "crt/stddef.bi"
#include "crt/sys/types.bi"
#include "MemoryMapLinux.bi"

'' Substitute for basic C-runtime and POSIX headers... fcntl.bi doesn't appear to work on Linux and mman.bi doesn't even exist
#define MAP_FILE &h00
#define MAP_FAILED Cast(Any Ptr, -1)
#define PROT_READ &h01
#define MAP_PRIVATE &h02
#define O_RDONLY &h00
Declare Function open_ Alias "open" (ByVal As Const ZString Ptr, ByVal As Long, ...) As Long
Declare Function mmap Alias "mmap" (ByVal As Any Ptr, ByVal As size_t, ByVal As Integer, ByVal As Integer, ByVal As Integer, ByVal As off_t) As Any Ptr
Declare Function munmap Alias "munmap" (ByVal As Any Ptr, ByVal As Integer) As Integer
Declare Function close_ Alias "close" (ByVal As Integer) As Integer
'' end mman.bi substitute

Function Poodle.MemoryMap.Open(Filename As String) As MemoryMap Pointer
    Var MemoryMapObject = New Poodle.MemoryMapLinux(Filename)
    Return Cast(MemoryMap Pointer, MemoryMapObject)    
End Function

Constructor Poodle.MemoryMapLinux(Filename As String)
    This.Status = Poodle.MemoryMap.MemoryMapInvalid
    
    Dim As Integer FileHandle = FreeFile
    If Open(Filename, For Binary, Access Read, As FileHandle) <> 0 Then
        This.FileData = 0
        Exit Constructor
    End If
    This.Size = Cast(Unsigned LongInt, Lof(FileHandle))
    Close FileHandle

    Dim As Integer FileDescriptor = open_(Filename, O_RDONLY)
    If FileDescriptor < 0 Then 
        This.FileData = 0
        Exit Constructor
    End If

    This.FileData = mmap(0, This.Size, PROT_READ, MAP_FILE Or MAP_PRIVATE, FileDescriptor, 0)
    close_(FileDescriptor)
    If This.FileData = MAP_FAILED Then
        This.FileData = 0
        Exit Constructor
    End If
    
    This.Status = Poodle.MemoryMap.MemoryMapValid
End Constructor

Function Poodle.MemoryMapLinux.GetData() As Unsigned Byte Pointer
    Return Cast(Unsigned Byte Pointer, This.FileData)
End Function

Function Poodle.MemoryMapLinux.GetSize() As Unsigned LongInt
    Return This.Size
End Function

Function Poodle.MemoryMapLinux.GetStatus() As Poodle.MemoryMap.MemoryMapStatus
    Return This.Status
End Function

Destructor Poodle.MemoryMapLinux()
    If This.FileData <> 0 Then
        munmap(This.FileData, This.Size)
    End If
End Destructor

