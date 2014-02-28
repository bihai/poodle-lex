import sys
sys.path.append("..")
import unittest
from Generator.CoverageSet import CoverageSet

class TestCoverageSet(unittest.TestCase):
    def test_overlap_removal(self):
        coverage_set = CoverageSet()
        coverage_set.add(25, 42)
        coverage_set.add(43, 46)
        coverage_set.add(16, 30)
        coverage_set.add(98, 101)
        coverage_set.add(18, 20)
        coverage_set.add(15, 16)
        intervals = [i for i in coverage_set]
        expected = [(15, 46), (98, 101)]
        for i, j in zip(intervals, expected):
            self.assertEqual(i, j)
            
    def test_segmentation(self):
        coverage_set = [CoverageSet() for i in xrange(3)]
        coverage_set[0].add(25, 42)
        coverage_set[0].add(15, 16)
        coverage_set[1].add(16, 30)
        coverage_set[1].add(30, 35)
        coverage_set[2].add(37, 40)
        coverage_set[2].add(39, 41)
        expected = [
            ((15, 15), set(['0'])),
            ((16, 16), set(['1', '0'])),
            ((17, 24), set(['1'])),
            ((25, 35), set(['1', '0'])),
            ((36, 36), set(['0'])),
            ((37, 41), set(['0', '2'])),
            ((42, 42), set(['0']))
        ]
        segments = CoverageSet.segments(*[(cset, str(i)) for i, cset in enumerate(coverage_set)])
        for ((expected_segment, expected_idset), (segment, idset)) in zip(expected, segments):
            self.assertEqual(expected_segment, segment)
            self.assertEqual(expected_idset, idset)
    
    def test_intersection(self):
        coverage_set = [CoverageSet() for i in xrange(3)]
        coverage_set[0].add(25, 42)
        coverage_set[0].add(15, 16)
        coverage_set[1].add(16, 30)
        coverage_set[1].add(30, 35)
        coverage_set[2].add(37, 40)
        coverage_set[2].add(39, 41)
        intersection = CoverageSet.intersection(*coverage_set)
        self.assertEqual([i for i in intersection], [])

        coverage_set[2].add(31, 36)
        intersection2 = CoverageSet.intersection(*coverage_set)
        self.assertEqual([i for i in intersection2], [(31, 35)])
        
    def test_union(self):
        coverage_set = [CoverageSet() for i in xrange(3)]
        coverage_set[0].add(25, 42)
        coverage_set[0].add(15, 16)
        coverage_set[1].add(16, 30)
        coverage_set[1].add(30, 35)
        coverage_set[1].add(99, 100)
        coverage_set[2].add(37, 40)
        coverage_set[2].add(39, 41)
        union = CoverageSet.union(*coverage_set)
        self.assertEqual([i for i in union], [(15, 42), (99, 100)])
        
    def test_difference(self):
        coverage_set = [CoverageSet() for i in xrange(3)]
        coverage_set[0].add(15, 30)
        coverage_set[0].add(35, 50)
        coverage_set[1].add(25, 40)
        coverage_set[1].add(45, 60)
        coverage_set[2].add(0, 5)
        coverage_set[2].add(10, 20)
        difference = CoverageSet.difference(coverage_set[0], *coverage_set[1:3])
        self.assertEqual([i for i in difference], [(21, 24), (41, 44)])
        
if __name__ == '__main__':
    unittest.main()