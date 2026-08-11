import numpy as np
from numpy import polynomial as poly

rng = np.random.default_rng()

bit = int(input("Enter a bit (0 or 1): "))

q = 97
n = 4


A =  rng.integers(0, q, size=n)
sA = rng.integers(0, q, size=(n))
eA = rng.integers(-1, 2, size=(n))


print(f'A Pub: {A}')
print(f's Priv: {sA}')
print(f'e Error: {eA}')

xN_1 = [1] + [0] * (n-1) + [1]

A = np.floor(np.polydiv(A, xN_1)[1]).astype(int)
bA = np.polymul(A, sA)%q
bA = np.floor(np.polydiv(bA, xN_1)[1]).astype(int)
bA = np.polyadd(bA, eA) % q
bA = np.floor(np.polydiv(bA, xN_1)[1]).astype(int)

print(f'A Pub (mod x^n + 1): {A}')
print(f'b Pub Key (mod x^n + 1): {bA}')

r = rng.integers(0, 2, size=(n))

u = np.polymul(r, A) % q
u = np.floor(np.polydiv(u, xN_1)[1]).astype(int)

v = np.polymul(r, bA) % q
v = np.floor(np.polydiv(v, xN_1)[1]).astype(int)
m = np.full(n, bit * (q // 2))
v = np.polyadd(v, m) % q
v = np.floor(np.polydiv(v, xN_1)[1]).astype(int)

print(f'Ciphertext: (u, v) = ({u}, {v})')

dec = np.polysub(v, np.polymul(sA, u)) % q
dec = np.floor(np.polydiv(dec, xN_1)[1]).astype(int)

dec = dec % q

votes = [1 if (q/4 <= c <3*q/4) else 0 for c in dec]
recovered_bit = round(sum(votes) / len(votes))

print(f'Decrypted value: {dec}')
print(f'Recovered bit: {recovered_bit}')




