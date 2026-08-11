import unittest

from MLKEM.params import n, q
from MLKEM.encoding import compress, decompress, byte_encode, byte_decode


class TestEncoding(unittest.TestCase):

    def test_compress_undoes_decompress(self):
        for d in (1, 4, 5, 10, 11):
            for y in range(2 ** d):
                self.assertEqual(compress(decompress([y], d), d), [y])

    def test_encode_round_trip(self):
        for d in (1, 4, 5, 10, 11):
            poly = [i % (2 ** d) for i in range(n)]
            self.assertEqual(byte_decode(byte_encode(poly, d), d), poly)

    def test_encode_round_trip_at_twelve_bits(self):
        poly = [i % q for i in range(n)]
        self.assertEqual(byte_decode(byte_encode(poly, 12), 12), poly)

    def test_encoded_length(self):
        poly = [0] * n
        for d in (1, 4, 5, 10, 11, 12):
            self.assertEqual(len(byte_encode(poly, d)), 32 * d)


if __name__ == "__main__":
    unittest.main()
