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

import collections
from orderedmultidict import omdict

from Lexer import RulesFileException

class Node(object):
    """
    Visitable object which contains a line number
    """
    def accept(self, visitor):
        self.throw("not implemented")
        
    def __init__(self, line_number):
        self.line_number = line_number
        
    def throw(self, message, is_sealed=False):
        """
        Throws an exception which refers to the line number
        @param message: the error message
        @param is_sealed: if True, tells exception wrappers not to wrap this in a similar exception
        """
        if self.line_number is None:
            raise RulesFileException(message, is_sealed)
        else:
            raise RulesFileException("On line %d, %s" % (self.line_number, message), is_sealed)
        
    @staticmethod
    def compare_nullable_icase(a, b):
        if a == b:
            return True
        if a is None or b is None:
            return False
        return a.lower() == b.lower()

class Scope(Node):
    """
    Object which can be used to find qualified names
    @ivar parent: Scope object representing the scope which contains this scope
    @ivar children: dictionary mapping lowercase string identifiers to Scope objects 
        representing which can be found from this scope
    @ivar resources: dictionary mapping string representing object types to other dictionaries.
        Each other dictionary maps a lowercase string identifier to an resource object, which
        can be multiple types.
    """
    def __init__(self, parent, line_number, **resources):
        Node.__init__(self, line_number)
        self.parent = parent
        self.children = {}
        self.resources = collections.defaultdict(omdict)
        for resource_type, resource_list in resources.items():
            for resource in resource_list:
                self.add(resource_type, resource)
        
    def add(self, type, resource):
        """
        Add an identifiable resource to the scope
        @param type: string identifying the type of resource to add
        @param resource: object representing the resource
        """
        caseless_id = resource.id.lower() if resource.id is not None else None
        self.resources[type].add(caseless_id, resource)
        
    def add_scope(self, type, scope):
        """
        Insert a child scope underneath this one
        @param type: string identifying the type of resource to add
        @param scope: object representing the child scope
        """
        self.add(type, scope)
        scope.parent = self
        if scope.id is not None:
            self.children[scope.id.lower()] = scope
        
    def all(self, type):
        return self.resources[type].allitems()
    
    def find(self, type, id, condition=None):
        """
        Find an object within a scope. 
        @param type: case-insensitive string represnting the type of object to find
        @param id: case-insensitive string representing the identifier of the object
        @return: a list of objects within the scope of the type specified and which have the id specified
        """
        if id == '':
            self.throw("invalid id '{0}'".format(id))
        
        if id is None:
            path = [None]
        else:
            path = [i.lower() for i in id.split('.')]
        directory = path[:-1]
        name = path[-1]
        scope = self
        
        # If an ID begins with '.', ignore the '.' and search from root
        if len(path) > 1 and path[0] == '':
            while scope.parent is not None:
                scope = scope.parent
            del path[0]
        if any(i == '' for i in path):
            self.throw("invalid id '{0}'".format(id))
        
        # Find scope from which to search
        if len(path) > 1:
            # Find first component
            while scope is not None:
                if path[0] in scope.children:
                    scope = scope.children[path[0]]
                    break
                scope = scope.parent
            if scope is None:
                return None
                
            # Find remaining components
            for path_id in path[1:-1]:
                if path_id not in scope.children:
                    return None
                scope = scope.children[path_id]
        
        # Find identifier from within the scope or its ancestors
        matches = []
        while scope is not None:
            if type in scope.resources:
                if name in scope.resources[type]:
                    matches.extend(scope.resources[type].getlist(name))
            scope = scope.parent
            
        if len(matches) == 0:
            return None
            
        return matches
        
    def __eq__(self, rhs):
        # Scope is equal if it has the same children and resources
        for resource_type in self.resources:
            if resource_type not in rhs.resources:
                return False
            for id in self.resources[resource_type]:
                if id not in rhs.resources[resource_type]:
                    return False
                if self.resources[resource_type].getlist(id) != rhs.resources[resource_type].getlist(id):
                    return False
        for child in self.children:
            if child not in rhs.children:
                return False
            if self.children[child] != rhs.children[child]:
                return False
                
        return True
