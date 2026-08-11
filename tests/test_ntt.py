import unittest
import numpy as np

from MLKEM.params import n, q
from MLKEM.ntt import ntt, ntt_inv, multiply_ntts, ZETAS


def schoolbook_multiply(a, b):
    c = np.convolve(a, b)
    for i in range(len(c) - 1, n - 1, -1):
        c[i - n] -= c[i]
    return c[:n] % q


class TestNTT(unittest.TestCase):

    def setUp(self):
        self.rng = np.random.default_rng(0)

    def random_poly(self):
        return self.rng.integers(0, q, n, dtype=np.int64)

    def test_zetas_match_the_standard(self):
        self.assertEqual(ZETAS[:4], [1, 1729, 2580, 3289])
        self.assertEqual(ZETAS[127], 2154)

    def test_inverse_undoes_the_transform(self):
        f = self.random_poly()
        self.assertTrue(np.array_equal(ntt_inv(ntt(f)), f))

    def test_multiplying_by_one_changes_nothing(self):
        f = self.random_poly()
        one = np.zeros(n, dtype=np.int64)
        one[0] = 1
        product = ntt_inv(multiply_ntts(ntt(f), ntt(one)))
        self.assertTrue(np.array_equal(product, f))

    def test_product_matches_plain_multiplication(self):
        f = self.random_poly()
        g = self.random_poly()
        product = ntt_inv(multiply_ntts(ntt(f), ntt(g)))
        self.assertTrue(np.array_equal(product, schoolbook_multiply(f, g)))


if __name__ == "__main__":
    unittest.main()
