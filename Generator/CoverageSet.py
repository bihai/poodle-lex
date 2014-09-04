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

import blist
import itertools

class CoverageSet(object):
    """
    Uses a set of intervals to define a numerical space. Stored as a sorted list
    """
    def __init__(self, intervals=[]):
        """
        @param intervals: a list of tuples, each with a minimum number and a maximum number representing a range of values covered by the set.
        """
        self.intervals = blist.sortedlist()
        self.dirty = False
        for min_v, max_v in intervals:
            self.add(min_v, max_v)
            
    def __iter__(self):
        self.remove_overlap()
        interval_endpoints = iter(self.intervals)
        while True:
            try:
                min_v, is_end = next(interval_endpoints)
                max_v, is_end = next(interval_endpoints)
                yield (min_v, max_v)
            except StopIteration:
                break
                
    def is_empty(self):
        return len(self.intervals) >= 2
    
    def merge_adjacent(self):
        """
        Internal method, merges intervals for which the maximum of one interval is one less than the minimum of another interval.
        """
        if len(self.intervals) < 4:
            return
        i = len(self.intervals)-4
        while i >= 0:
            if self.intervals[i+1][0] == self.intervals[i+2][0]-1:
                min_v, is_end = self.intervals[i]
                max_v, is_end = self.intervals[i+3]
                del self.intervals[i:i+4]
                self.add(min_v, max_v)
            i -= 2
    
    def remove_overlap(self):
        """
        Internal method. Merges overlapping intervals.
        """
        reverse_enumerate = lambda l: itertools.izip(xrange(len(l)-1, -1, -1), reversed(l))
        if self.dirty:
            level = 0
            did_remove = False
            to_delete = []
            for i, (value, is_end) in reverse_enumerate(self.intervals):
                if is_end == 1:
                    if level > 0:
                        to_delete.append(i)
                        did_remove = True
                    level += 1
                else:
                    if level > 1:
                        to_delete.append(i)
                        did_remove = True
                    level -= 1
            for index in to_delete:
                del self.intervals[index]
            self.merge_adjacent()
            self.dirty = False
            return did_remove
        return False

    def add(self, min_v, max_v):
        """
        Addes an ranges of values to the set's coverage.
        
        @param min_v: the inclusive minimum value covered by the range.
        @param max_v: the inclusive maximum value covered by the range.
        """
        self.intervals.update(((min_v, 0), (max_v, 1)))
        self.dirty = True
        
    def remove(self, min_v, max_v):
        """
        Removes a range of values to the set's coverage. 
        Any invervals that intersect this range will either be shortened or removed.
        
        @param min_v: the inclusive minimum value of the range to be removed.
        @param max_v: the inclusive maximum value of the range to be removed.
        """
        self.remove_overlap()
        before_min = self.intervals.bisect_left((min_v, 0))
        after_max = self.intervals.bisect_right((max_v, 1))
        if after_max == 0 or before_min == len(self.intervals):
            return
        if (after_max - before_min) & 0x01 == 0:
            min_value, min_is_end = self.intervals[before_min]
            max_value, max_is_end = self.intervals[after_max-1]
            del self.intervals[before_min:after_max]
            if min_is_end == 1 and max_is_end == 0:
                self.intervals.add((min_v-1, 1))
                self.intervals.add((max_v+1, 0))
        else:
            min_value, min_is_end = self.intervals[before_min]
            del self.intervals[before_min:after_max]
            if min_is_end == 0:
                self.intervals.add((max_v + 1, 0))
            else:
                self.intervals.add((min_v - 1, 1))

    def update(self, *other_coverage_sets):
        """
        Adds to the set's coverage the values covered by one or more other CoverageSet objects.
        
        @param other_coverage_sets: one or more CoverageSet objects, the coverage of which will be added to this object.
        """
        for coverage_set in other_coverage_sets:
            self.intervals.update(coverage_set.intervals)
        self.dirty = True
        
    def difference_update(self, *other_coverage_sets):
        """
        Removes from the set's coverage the values covered by one or more other CoverageSet object.
        @param other_coverage_sets: one or more CoverageSet objects, the coverage of which will be removed from this object.
        """
        for coverage_set in other_coverage_sets:
            coverage_set.remove_overlap()
            for i in xrange(0, len(coverage_set.intervals), 2):
                (min_v, min_is_end), (max_v, max_is_end) = coverage_set.intervals[i:i+2]
                self.remove(min_v, max_v)
                
    def __eq__(self, other_coverage_set):
        self.remove_overlap()
        other_coverage_set.remove_overlap()
        return self.intervals == other_coverage_set.intervals
    
    def __ne__(self, other_coverage_set):
        return not (self == other_coverage_set)
        
    def __hash__(self):
        self.remove_overlap()
        return hash(tuple(sorted(i for i in self)))
    
    def __str__(self):
        def format_codepoint(codepoint):
            if codepoint == ord('"'):
                return "'\\\"'"
            if codepoint in xrange(32, 127):
                return "'%s'" % chr(codepoint)
            else:
                return "0x%x" % codepoint
                
        def remove_duplicates(intervals):
            if intervals[0] == intervals[1]:
                return format_codepoint(intervals[0])
            else:
                return "%s-%s" % tuple([format_codepoint(i) for i in intervals])
                
        #self.remove_overlap()
        return "CoverageSet([%s])" % ", ".join([repr(remove_duplicates(i)) for i in self])
    
    def __repr__(self):
        return str(self)
    
    def intersection_update(self, *other_coverage_sets):
        """
        Removes all values from this set's coverage, except for those which are also covered by one or more other CoverageSet objects 
        
        @param other_coverage_sets: one or more other CoverageSet objects.
        """
        reverse_enumerate = lambda l: itertools.izip(xrange(len(l)-1, -1, -1), reversed(l))
        for other_coverage_set in other_coverage_sets:
            other_coverage_set.remove_overlap()
        self.update(*other_coverage_sets)
        IDLE=0
        EXPECT_MAX=1
        EXPECT_MIN=2
        new_intervals = blist.sortedlist()
        state = IDLE
        level = 0
        for i, (value, is_end) in reverse_enumerate(self.intervals):
            if is_end == 1:
                level += 1
            else:
                level -= 1
            if state == IDLE:
                if level == len(other_coverage_sets)+1:
                    new_intervals.add((value, is_end))
                    state = EXPECT_MIN
            elif state == EXPECT_MIN:
                if is_end == 0:
                    new_intervals.add((value, is_end))
                    state = EXPECT_MAX
                else:
                    state = IDLE
            elif state == EXPECT_MAX:
                if is_end == 1:
                    new_intervals.add((value, is_end))
                    state = EXPECT_MIN
                else:
                    state = IDLE
        self.intervals = new_intervals
    
    @staticmethod
    def union(*coverage_sets):
        """
        Returns a new CoverageSet object that covers all the values covered by one or more other CoverageSet objects.
        
        @param coverage_sets: one or more other CoverageSet objects.
        """
        new_coverage_set = CoverageSet()
        new_coverage_set.update(*coverage_sets)
        return new_coverage_set
        
    @staticmethod
    def difference(first_coverage_set, *other_coverage_sets):
        """
        Returns a new CoverageSet object that covers the values covered by a set, except for those covered by one or more other CoverageSet objects.
        
        @param first_coverage_set: CoverageSet object representing a range of values
        @param other_coverage_sets: CoverageSet objects representing ranges of values to exclude
        """
        new_coverage_set = CoverageSet()
        new_coverage_set.update(first_coverage_set)
        new_coverage_set.difference_update(*other_coverage_sets)
        return new_coverage_set
    
    @staticmethod
    def intersection(*coverage_sets):
        """
        Returns a new CoverageSet object that covers only the values covered by all of the input CoverageSet objects.
        
        @param coverage_sets: CoverageSet objects representing the ranges of values to intersect
        """
        new_coverage_set = CoverageSet()
        if len(coverage_sets) != 0:
            new_coverage_set.update(coverage_sets[0])
            new_coverage_set.intersection_update(*coverage_sets[1:])
        return new_coverage_set
    
    @staticmethod
    def segments(*coverage_sets_and_ids):
        """
        Takes in one or more CoverageSet objects mapped to identifiers, and returns contiguious 
        numerical intervals which are covered by one or more of the coverage sets, along with 
        a list of identifiers representing CoverageSet objects which cover each interval.
        @param coverage_sets_and_ids: one or more tuples with the first element being a CoverageSet
            objects, and the second being an identifier for the coverage set.
        @return: an iterator which returns a tuple with two elements. The first element of 
            each tuple is a tuple with two integers representing respectively the inclusive minimum 
            value and inclusive maximum value of the interval. The second element is a list of 
            identifiers, each representing a CoverageSet object that covers the interval.
        """
        for coverage_set, set_id in coverage_sets_and_ids:
            coverage_set.remove_overlap()
        endpoint_lists_with_ids = [zip(coverage_set.intervals, [set_id]*len(coverage_set.intervals)) for coverage_set, set_id in coverage_sets_and_ids]
        unified = blist.sortedlist()
        for item in endpoint_lists_with_ids:
            unified.update(item)
        unified_iter = iter(unified)
        (last_value, last_is_end), set_id = next(unified_iter)
        level = 1
        set_ids = set([set_id])
        for (value, is_end), set_id in unified_iter:
            if level > 0:
                if value == last_value + 1 and is_end == 0 and last_is_end == 1:
                    pass
                elif value == last_value and is_end == 1 and last_is_end == 0:
                    yield (last_value, value), frozenset(set_ids)
                elif value != last_value:
                    if is_end == 0 and last_is_end == 0:
                        yield (last_value, value-1), frozenset(set_ids)
                    elif is_end == 0 and last_is_end == 1:
                        yield (last_value+1, value-1), frozenset(set_ids)
                    elif is_end == 1 and last_is_end == 0:
                        yield (last_value, value), frozenset(set_ids)
                    elif is_end == 1 and last_is_end == 1:
                        yield (last_value+1, value), frozenset(set_ids)
            if is_end == 0:
                level += 1
                set_ids.add(set_id)
            else:
                level -= 1
                set_ids.remove(set_id)
            last_value, last_is_end = value, is_end
        
    def __contains__(self, value):
        if isinstance(value, CoverageSet):
            return CoverageSet.intersection(self, value) == value
        else:
            self.remove_overlap()
            before_min = self.intervals.bisect_left((value, 1))
            if before_min == len(self.intervals):
                return False
            return self.intervals[before_min][1] == 1
        
    def __len__(self):
        self.remove_overlap()
        n = 0
        for i in xrange(0, len(self.intervals), 2):
            (min_v, min_is_end), (max_v, max_is_end) = self.intervals[i:i+2]
            n += max_v - min_v + 1
        return n
        