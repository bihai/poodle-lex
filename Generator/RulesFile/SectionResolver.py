# Copyright (C) 2014 Parker Michaels
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

from Visitor import Visitor

class SectionResolver(Visitor):
    """
    Resolve a Section object or a SectionReference object into a full blown section
    @ivar section: the resolved Section object, after visiting a Section or SectionReference object
    """
    @staticmethod
    def resolve(section, scope):
        """
        Static method for resolving scopes
        @param section: Section or SectionReference object which is to be resolved
        @param scope: containing Scope object (typically a section)
        @return: Section object which section represents
        """
        resolver = SectionResolver(scope)
        section.accept(resolver)
        return resolver.section
    
    def __init__(self, scope):
        self.section = None
        self.scope = scope
        
    def visit_section(self, section):
        self.section = section
        
    def visit_section_reference(self, section_reference):
        sections = self.scope.find('section', section_reference.name)
        if sections is None:
            return
        self.section = sections[0]
