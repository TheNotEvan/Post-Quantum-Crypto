import numpy as np
from numpy import polynomial as poly


rng = np.random.default_rng()

n = 256
q = 3329
k = 4
B = 1 

def poly_reduce(c):
    c = c.copy()
    for i in range(len(c) - 1, n-1, -1):
        c[i-n] -= c[i]
    
    return c[:n]

def poly_mul(a ,b):
    return poly_reduce(np.convolve(a,b)) % q 

def poly_add(a, b):
    return (a + b) % q

def rand_poly(low, high):
    return rng.integers(low, high, size = n)

def mat_vec_mul(M, v):
    out = np.zeros((k,n), dtype=int)
    for i in range(k):
        acc = np.zeros(n, dtype = int)
        for j in range(k):
            acc = poly_add(acc, poly_mul(M[i,j], v[j]))
        out[i] = acc
    return out


def vec_dot(u,v):
    acc = np.zeros(n, dtype=int)
    for i in range(k):
        acc = poly_add(acc, poly_mul(u[i], v[i]))
    return acc

A = np.array([[rand_poly(0,q) for _ in range (k)] for _ in range (k)])
# Generation of secret key vector (k,n), consisting of k polynomials of the nth power
S0 = np.array([rand_poly(-B, B + 1) for _ in range (k)])
E0 = np.array([rand_poly(-B, B+1) for _ in range (k)])

P0 = mat_vec_mul(A, S0)
for i in range (k):
    P0[i] = poly_add(P0[i],E0[i])

message = rand_poly(0, 2)
S1 = np.array([rand_poly(-B, B + 1) for _ in range(k)])
E1 = np.array([rand_poly(-B, B + 1) for _ in range (k)])
E2 = rand_poly(-B, B + 1)

AT = np.transpose(A, (1,0,2))
u = mat_vec_mul(AT, S1)
for i in range(k):
    u[i] = poly_add(u[i], E1[i])
 
v = vec_dot(P0, S1)
v = poly_add(v, E2)
v = poly_add(v, message * (q//2))

ciphertext = (u,v)

# Decryption

rec_message = vec_dot(u, S0)
rec_message = poly_add(v, -rec_message)
rec_message = ((rec_message  + (q//4)) // (q//2)) % 2

print(f'message: {message}')
print(f'Recovered: {rec_message}')
print(f'Match: {np.array_equal(rec_message, message)}')


