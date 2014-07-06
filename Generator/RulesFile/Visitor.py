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

class ScopedId(object):
    """
    Hashable ID that can be tested for subsets, and indexed into parts
    """
    def __init__(self, ids):
        """
        @param ids: a list of strings, each representing a single ID components
        """
        self.ids = tuple(ids)
    
    def __hash__(self):
        return hash(self.ids)
    
    def __eq__(self, rhs):
        if isinstance(rhs, tuple):
            return self.ids == rhs
        else:
            return self.ids == rhs.ids
        
    def __getitem__(self, index):
        return self.ids[index]
        
    def __contains__(self, rhs):
        zipped = zip(self.ids, rhs.ids)
        if len(zipped) != len(self.ids) or len(rhs.ids) == len(self.ids):
            return False
        return all(i == j for i, j in zipped)
        
    def __iter__(self):
        return iter(self.ids)
    
    def __len__(self):
        return len(self.ids)
    
    def __repr__(self):
        return "ScopedId('%s')" % "', '".join(self.ids)
        
class Visitor(object):
    """
    Base visitor for rules file nodes.
    """
    def __init__(self):
        self.traverser = None
    
    def visit_rule(self, rule):
        pass
    
    def visit_define(self, define): 
        pass
        
    def visit_section(self, section):
        pass
        
    def leave_section(self, section):
        """
        Called when a traverser object moves up the section hierarchy.
        @param section: The section being left
        """
        pass
        
    def visit_section_reference(self, section_reference):
        pass
        
    def visit_reserved_id(self, reserved_id):
        pass

class Traverser(Visitor):
    """
    Visitor class which traverses the rules file AST and pulls in other visitors at each node.
    Provides scope to other visitors
    """
    def __init__(self, *visitors):
        self.visitors = visitors
        for visitor in visitors:
            visitor.traverser = self
        self.section = []
        
    def get_scoped_id(self, id=None):
        """
        Provides the current scope of the traverser
        @param id: Optional local identifier to add to the scope.
        @return: A ScopedId object representing the scope
        """
        id_parts = [i.id for i in self.section]
        if id is not None:
            id_parts.append(id)
        return ScopedId(id_parts)
        
    def visit_rule(self, rule):
        for visitor in self.visitors:
            rule.accept(visitor)
        if rule.section_action is not None:
            if rule.section_action[1] is not None:
                rule.section_action[1].accept(self)
            
    def visit_define(self, define):
        for visitor in self.visitors:
            define.accept(visitor)
            
    def visit_reserved_id(self, reserved_id):
        for visitor in self.visitors:
            reserved_id.accept(visitor)
                    
    def visit_section(self, section):
        for visitor in self.visitors:
            section.accept(visitor)
            
        self.section.append(section)
        for id, rule in section.all('rule'):
            rule.accept(self)
        for id, define in section.all('define'):
            define.accept(self)
        for id, subsection in section.all('section'):
            subsection.accept(self)
        section = self.section.pop()
        
        for visitor in self.visitors:
            visitor.leave_section(section)
    
    def visit_section_reference(self, section_reference):
        for visitor in self.visitors:
            section_reference.accept(visitor)
            