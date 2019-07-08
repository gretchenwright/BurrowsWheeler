import unittest
import filecmp

from BWIndex import BWIndex


class TestBWIndex(unittest.TestCase):

    def test_small_index(self):
        BWIndex('small_index.txt', genomefile='genome.txt', countgap=100, suffixgap=100)
        self.assertTrue(filecmp.cmp('small_index.txt', 'small_index_baseline.txt'))

    def test_index_genome_as_string(self):
        BWIndex('small_index_from_string.txt', genome='ATGCATCGATCGATCATCATCGATCGATCG$', countgap=100, suffixgap=100)
        self.assertTrue(filecmp.cmp('small_index_from_string.txt', 'small_index_from_string_baseline.txt'))


if __name__ == '__main__':
    unittest.main()
