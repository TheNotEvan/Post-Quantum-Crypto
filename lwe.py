import readline
import numpy as np

rng = np.random.default_rng()

bit = int(input("Enter a bit (0 or 1): "))

n = 8
q = 97
B = 1
m = 16

A = rng.integers(0, q, size =(m,n))

print (f'A Matrix: {A}')

s = rng.integers(0, q, size = (n))

print(f's Array: {s}')

e = rng.integers(-B, B + 1, size = m)

print(f'e Array: {e}')

b = (A @ s + e) % q

print(f'B Array: {b}')

r = rng.integers(0, 2, size = m)

u = (r @ A) % q

v = (r @ b + bit * (q // 2)) % q

print(f'Ciphertext: (u, v) = ({u}, {v})')

dec = v - s @ u
dec = dec % q

print(f'Decrypted value: {dec}')

if dec < q//2:
    print("Decrypted bit: 0")
elif dec >= q//2:
    print("Decrypted bit: 1")

