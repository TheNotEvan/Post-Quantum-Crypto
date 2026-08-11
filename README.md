# Post Quantum Crypto

A python implementation of a LWE (Learning with Errors), Ring-LWE, Module-LWE, and ML-KEM (Module Lattice Key Encapsulation Mechanism) algorithims, with ML-KEM implemented as standarized in NIST FIPS 203.

Made by a high school student interested in post-quantum cryptography.

## 🚨 Warning 🚨

This program is meant for educational purposes only, and has not been security audits. Please do not use this in any real world environment. 

## Features

* ML-KEM Implementation: Full implementation of all three variants of ML-KEM (512,768,1024)
* ML-KEM-768 Demo: Script that encrypts an inputted message with the shared secret key and a nonce, then decrypts it.
* LWE, Ring-LWE, and Module-lWE: Full implementation of three algorithims based on Elucyada's videos on YouTube 

## Quick Start

```bash
git clone https://github.com/TheNotEvan/Post-Quantum-Crypto
cd Post-Quantum-Crypto
pip install -r requirements.txt
```

## Run 

### ML-KEM

```python
from MLKEM.params import ML_KEM_512, ML_KEM_768, ML_KEM_1024
from MLKEM.kem import ml_kem_key_gen, ml_kem_encaps, ml_kem_decaps

#Alice creates a public encapsulation key and private decapsulation key
ek, dk = ml_kem_key_gen(ML_KEM_768)
#Bob generates a shared secret key and ciphetext using the encapsulation key
K_bob, c = ml_kem_encaps(ek, ML_KEM_768)
#Alice uses the ciphertext to recover the shared secret key with the decapsulation key
K_alice = ml_kem_decaps(dk, c, ML_KEM_768)

print("Bob:  ", K_bob.hex())
print("Alice:", K_alice.hex())
print("match:", K_alice == K_bob)
```

### Run Demo

```bash
python MLKEM768Demo.py
```

### Run Test

Run all of the tests from the project root:

```bash
python -m unittest discover
```

Run a single file:

```bash
python -m unittest tests.test_kem
```

