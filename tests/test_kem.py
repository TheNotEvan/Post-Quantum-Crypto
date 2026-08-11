import unittest

from MLKEM.params import ML_KEM_512, ML_KEM_768, ML_KEM_1024
from MLKEM.kem import ml_kem_key_gen, ml_kem_encaps, ml_kem_decaps

PARAMETER_SETS = (ML_KEM_512, ML_KEM_768, ML_KEM_1024)


class TestKEM(unittest.TestCase):

    def test_both_sides_agree_on_the_secret(self):
        for p in PARAMETER_SETS:
            ek, dk = ml_kem_key_gen(p)
            K_bob, c = ml_kem_encaps(ek, p)
            K_alice = ml_kem_decaps(dk, c, p)
            self.assertEqual(K_alice, K_bob)

    def test_key_and_ciphertext_sizes(self):
        for p in PARAMETER_SETS:
            ek, dk = ml_kem_key_gen(p)
            K, c = ml_kem_encaps(ek, p)
            self.assertEqual(len(ek), p.ek_bytes)
            self.assertEqual(len(dk), p.dk_bytes)
            self.assertEqual(len(c), p.ct_bytes)
            self.assertEqual(len(K), p.ss_bytes)

    def test_every_keypair_is_different(self):
        ek1, dk1 = ml_kem_key_gen(ML_KEM_768)
        ek2, dk2 = ml_kem_key_gen(ML_KEM_768)
        self.assertNotEqual(ek1, ek2)
        self.assertNotEqual(dk1, dk2)

    def test_changed_ciphertext_gives_a_different_secret(self):
        ek, dk = ml_kem_key_gen(ML_KEM_768)
        K, c = ml_kem_encaps(ek, ML_KEM_768)
        tampered = bytearray(c)
        tampered[0] = tampered[0] ^ 1
        self.assertNotEqual(ml_kem_decaps(dk, bytes(tampered), ML_KEM_768), K)


if __name__ == "__main__":
    unittest.main()
