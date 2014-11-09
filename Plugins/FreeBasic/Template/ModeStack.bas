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

$MODE_INCLUDE

Constructor $NAMESPACE.$MODE_STACK_CLASS_NAME()
    This.Stack = 0
    This.Reset()
End Constructor

Property $NAMESPACE.$MODE_STACK_CLASS_NAME.Mode() As $TYPE_MODE
    Return This.Stack[This.Index]
End Property

Sub $NAMESPACE.$MODE_STACK_CLASS_NAME.Reset()
    This.Index = 0
    If This.Stack = 0 Then
        Delete This.Stack
    End If
    This.Capacity = 16
    This.Stack = New ModeId[This.Capacity]
    This.Stack[This.Index] = $INITIAL_MODE_ID    
End Sub

Sub $NAMESPACE.$MODE_STACK_CLASS_NAME.EnterSection(ByVal Id As $TYPE_MODE)
    If This.Index = This.Capacity-1 Then
        ' Expand the stack
        Var NewCapacity = This.Capacity * 2
        Var NewStack = New ModeId[NewCapacity]
        For i As Integer = 0 To This.Capacity - 1
            NewStack[i] = This.Stack[i]
        Next i
        Delete This.Stack
        This.Stack = NewStack
        This.Capacity = NewCapacity
    End If
    This.Index += 1
    This.Stack[This.Index] = Id
End Sub

Sub $NAMESPACE.$MODE_STACK_CLASS_NAME.ExitSection()
    If This.Index > 0 Then This.Index -= 1
End Sub

Sub $NAMESPACE.$MODE_STACK_CLASS_NAME.SwitchSection(ByVal Id As $TYPE_MODE)
    This.Stack[This.Index] = Id
End Sub
