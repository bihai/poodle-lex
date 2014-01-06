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
	
	def merge_adjacent(self):
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
		reverse_enumerate = lambda l: itertools.izip(xrange(len(l)-1, -1, -1), reversed(l))
		if self.dirty:
			level = 0
			did_remove = False
			for i, (value, is_end) in reverse_enumerate(self.intervals):
				if is_end == 1:
					if level > 0:
						del self.intervals[i]
						did_remove = True
					level += 1
				else:
					if level > 1:
						del self.intervals[i]
						did_remove = True
					level -= 1
			self.merge_adjacent()
			self.dirty = False
			return did_remove
		return False

	def add(self, min_v, max_v):
		self.intervals.update(((min_v, 0), (max_v, 1)))
		self.dirty = True
		
	def remove(self, min_v, max_v):
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
		for coverage_set in other_coverage_sets:
			self.intervals.update(coverage_set.intervals)
		self.dirty = True
		
	def difference_update(self, *other_coverage_sets):
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
		return hash(frozenset(i for i in self))
	
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
		self.remove_overlap()
		return "CoverageSet([%s]" % ", ".join([repr(remove_duplicates(i)) for i in self])
	
	def __repr__(self):
		return str(self)
	
	def intersection_update(self, *other_coverage_sets):
		reverse_enumerate = lambda l: itertools.izip(xrange(len(l)-1, -1, -1), reversed(l))
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
		
	def union(self, *other_coverage_sets):
		new_coverage_set = CoverageSet()
		new_coverage_set.update(self)
		new_coverage_set.update(*other_coverage_sets)
		return new_coverage_set
		
	def difference(self, *other_coverage_sets):
		new_coverage_set = CoverageSet()
		new_coverage_set.update(self)
		new_coverage_set.difference_update(*other_coverage_sets)
		return new_coverage_set
	
	def intersection(self, *other_coverage_sets):
		new_coverage_set = CoverageSet()
		new_coverage_set.update(self)
		new_coverage_set.intersection_update(*other_coverage_sets)
	
	@staticmethod
	def segments(*coverage_sets_and_ids):
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
			if level > 0 and ((last_value, last_is_end) != (value, is_end)):
				if is_end == 0 and last_is_end == 0:
					yield (last_value, value-1), set_ids
				elif is_end == 0 and last_is_end == 1:
					yield (last_value+1, value-1), set_ids
				elif is_end == 1 and last_is_end == 0:
					yield (last_value, value), set_ids
				elif is_end == 1 and last_is_end == 1:
					yield (last_value+1, value), set_ids
			if is_end == 0:
				level += 1
				set_ids.add(set_id)
			else:
				level -= 1
				set_ids.remove(set_id)
			last_value, last_is_end = value, is_end
		
	def __contains__(self, value):
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
