
#Basic implementation of Module LWE, a public key cryptosystem believed to be safe against attacks by theoretical powerful quantumn computers.
#This implementation is not secure and is for educational purposes only. Do not use this program with real data. 
#Thanks to Elucyada for his explanation on Module LWE, which can be found at https://www.youtube.com/watch?v=lVQuV1sfSw4

import numpy as np
rng = np.random.default_rng()


#Constants. Ensure that q is a prime number.
n = 256
q = 3329
k = 4
B = 1 

#Reduce an arbitary length coefficent aray mod (x^n +1)
def poly_reduce(c):
    c = c.copy()
    for i in range(len(c) - 1, n-1, -1):
        c[i-n] -= c[i]
    
    return c[:n]

#Multiply two ring elements mod (x^n +1, q) of length n
def poly_mul(a ,b):
    return poly_reduce(np.convolve(a,b)) % q 

#Add two vectors mod q
def poly_add(a, b):
    return (a + b) % q

#Generate n random integrs from range [low, high)
def rand_poly(low, high):
    return rng.integers(low, high, size = n)

#Multiply a matrix M of rings of the nth power (k,k,n) by a vector of rings of the nth power (k,n). Output is a vector (k,n). 
def mat_vec_mul(M, v):
    out = np.zeros((k,n), dtype=int)
    for i in range(k):
        acc = np.zeros(n, dtype = int)
        for j in range(k):
            acc = poly_add(acc, poly_mul(M[i,j], v[j]))
        out[i] = acc
    return out

#Multiply a vector u by a vector v, outputing a ring to the nth power. 
def vec_dot(u,v):
    acc = np.zeros(n, dtype=int)
    for i in range(k):
        acc = poly_add(acc, poly_mul(u[i], v[i]))
    return acc

#Matrix A (k,k,n) of ring elements 
A = np.array([[rand_poly(0,q) for _ in range (k)] for _ in range (k)])
# Generation of secret key vector (k,n), consisting of k rings 
S0 = np.array([rand_poly(-B, B + 1) for _ in range (k)])
#Noise
E0 = np.array([rand_poly(-B, B+1) for _ in range (k)])

#Creation of public key, which is A, P0. P0 is generated with the formula P0 := A @ S0 + E0
P0 = mat_vec_mul(A, S0)
for i in range (k):
    P0[i] = poly_add(P0[i],E0[i])

#Message to be encrypted
message = rand_poly(0, 2)
S1 = np.array([rand_poly(-B, B + 1) for _ in range(k)])
E1 = np.array([rand_poly(-B, B + 1) for _ in range (k)])
E2 = rand_poly(-B, B + 1)

#Creation of randomized masking component of the ciphertext u with formula u := A @ S1 + E1
AT = np.transpose(A, (1,0,2))
u = mat_vec_mul(AT, S1)
for i in range(k):
    u[i] = poly_add(u[i], E1[i])
 
#Creation of secret message v with formula v := (q//2) * message + E2 + <S1 @ P0>
v = vec_dot(P0, S1)
v = poly_add(v, E2)
v = poly_add(v, message * (q//2))

ciphertext = (u,v)

# Decryption
#Recover message using the formula message = [2/q(v - <S0 @ u>)]. This formula simplifies to the message plus noise, which is then rounded to determine if each bit is a zero or a one. 
rec_message = vec_dot(u, S0)
rec_message = poly_add(v, -rec_message)
rec_message = ((rec_message  + (q//4)) // (q//2)) % 2

print(f'message: {message}')
print(f'Recovered: {rec_message}')
print(f'Match: {np.array_equal(rec_message, message)}')


