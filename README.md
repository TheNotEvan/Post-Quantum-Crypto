# Post Quantum Crypto

A Python implementation of a LWE (Learning with Errors), Ring-LWE, Module-LWE, and ML-KEM (Module Lattice Key Encapsulation Mechanism) algorithims, with ML-KEM implemented as standardized in NIST FIPS 203.

Made by a high school student interested in post-quantum cryptography.

##  Notice 
> [!Note]
> This program is meant for educational purposes only, and has not been security audited. Please do not use this in any real-world environment. Except for the tests, all code in this project was my original work generated without the use of AI. In my ModuleLWE, I left comments that I originally intended to help me remember the math associated with the algorithim. I've left them there in order to show my full learning process, as well as the code for my LWE, which is a little messy. 


## Features

* ML-KEM Implementation: Full implementation of all three variants of ML-KEM (512,768,1024)
* ML-KEM-768 Demo: Script that encrypts an inputted message with the shared secret key and a nonce, then decrypts it.
* LWE, Ring-LWE, and Module-LWE: Full implementation of three algorithims based on Elucyada's videos on YouTube 

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
#Bob generates a shared secret key and ciphertext using the encapsulation key
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

