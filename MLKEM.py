import numpy as np
import hashlib
import secrets

n = 256
q = 3329
k = 3

eta1, eta2 = 2,2

du, dv = 10,4


class XOF:
    def __init__ (self):
        self._ctx = hashlib.shake_128()
        self._pos = 0
        self._buf = b''

    def absorb(self, data: bytes):
        self._ctx.update(data)
        self._pos = 0
        self._buf = b''
        return self

    def squeeze(self, num_bytes: int) -> bytes:
        end = self._pos + num_bytes
        if end > len(self._buf):
            new_len = max(end, len(self._buf) * 2, 512)
            self._buf = self._ctx.digest(new_len)
        out = self._buf[self._pos:end]
        self._pos = end
        return out
        
#Polynomial Arithmetic

def poly_add(a, b):
    return (a + b) % q

def poly_reduce(c):
    c = c.copy()
    for i in range(len(c) - 1, n-1, -1):
        c[i-n] -= c[i]
    
    return c[:n]

def poly_mul(a ,b):
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    return poly_reduce(np.convolve(a, b)) % q

def mat_vec_mul(M, v):
    out = np.zeros((k,n), dtype=np.int64)
    for i in range(k):
        acc = np.zeros(n, dtype = np.int64)
        for j in range(k):
            acc = poly_add(acc, poly_mul(M[i,j], v[j]))
        out[i] = acc
    return out

def vec_dot(u,v):
    acc = np.zeros(n, dtype=np.int64)
    for i in range(k):
        acc = poly_add(acc, poly_mul(u[i], v[i]))
    return acc


def compress(poly,d):
    return [(((x << d) + (q//2)) // q) % (1 << d) for x in poly]

def decompress(poly , d):
    return [(((q * y) + (1 << (d-1))) >> d)  for y in poly]

def bits_to_bytes(bits, length):
    B = [0] * length
    for i in range(8 * length):
        B[i//8] = B[i//8] + bits[i] * (2 ** (i % 8))
    return bytes(B)

def bytes_to_bits(B, length):
    C = list(B)
    b = [0] * (length  * 8)
    for i in range(length):
        for j in range(8):
            b[(8 * i) + j] = C[i] % 2
            C[i] = (C[i] // 2)
    return b

def byte_encode(poly, d):
    m = q if d == 12 else 2 ** d
    assert all(0 <= x < m for x in poly)
    b = [0] * (256 * d)
    for i in range(n):
        a = poly[i]
        for j in range(d):
            b[(i * d) + j] = a % 2 
            a = (a-b[(i*d) + j]) // 2
    B = bits_to_bytes(b, 32 * d)
    return B

def byte_decode(B, d):
    b = bytes_to_bits(B, d * 32)
    m = q if d == 12 else 2 ** d
    F = [0] * 256
    for i in range(n):
        val = 0
        for j in range(d):
            val += b[(i * d) + j] * (2 ** j)
        F[i] = val % m
    return F

def Sample_NTT(B):
    j = 0
    a = [0] * n 
    xof = XOF()
    xof.absorb(B)
    while j < n:
        C = xof.squeeze(3)
        d1 = C[0] + (256 * (C[1] % 16))
        d2 = (C[1]//16) + (16 * C[2])
        if d1 < q:
            a[j] = d1
            j += 1
        if d2 < q and j < n:
            a[j] = d2
            j += 1
    return a

def sample_poly_CBD(B):
    b = bytes_to_bits(B, len(B))
    f = [0] * n
    for i in range(n):
        x, y = 0,0
        for j in range(eta1):
            x += b[(2 * i * eta1) + j]
            y += b[(2 * i * eta1) + eta1 + j]
        f[i] = (x - y) % q
    return f 

def key_gen(d):
    digest = hashlib.sha3_512(d + bytes([k])).digest()
    rho, sigma = digest[:32], digest[32:]
    N = 0
    A = np.zeros((k,k,n), dtype=np.int64)
    for i in range(k):
        for j in range(k):
            A[i,j] = Sample_NTT(rho + bytes([j]) + bytes([i]))

    S = np.zeros((k,n), dtype=np.int64)
    E = np.zeros((k,n), dtype=np.int64)
    for i in range(k):
        S[i] = sample_poly_CBD(hashlib.shake_256(sigma + bytes([N])).digest(eta1 * 64))
        N += 1

    for i in range(k):
        E[i] = sample_poly_CBD(hashlib.shake_256(sigma + bytes([N])).digest(eta1 * 64))
        N += 1

    t  = mat_vec_mul(A, S)
    for i in range(k):
        t[i] = poly_add(t[i], E[i])

    epke = b''.join([byte_encode(t[i], 12) for i in range(k)]) + rho
    dpke = b''.join([byte_encode(S[i], 12) for i in range(k)])

    return epke, dpke

def encrypt(epke, m, r):
    N = 0
    t = [np.array(byte_decode(epke[i * 384:(i + 1) * 384], 12), dtype=np.int64)
         for i in range(k)]
    rho = epke[384*k:384*k + 32]
    A = np.zeros((k,k,n), dtype=np.int64)
    y = np.zeros((k,n), dtype=np.int64)
    e1 = np.zeros((k,n), dtype=np.int64)
    for i in range(k):
        for j in range(k):
            A[i,j] = Sample_NTT(rho + bytes([j]) + bytes([i]))

    for i in range(k):
        y[i] = sample_poly_CBD(hashlib.shake_256(r + bytes([N])).digest(eta1 * 64))
        N += 1

    for i in range(k):
        e1[i] = sample_poly_CBD(hashlib.shake_256(r + bytes([N])).digest(eta1 * 64))
        N += 1
    e2 = sample_poly_CBD(hashlib.shake_256(r + bytes([N])).digest(eta1 * 64))
    AT = np.transpose(A, (1,0,2))
    u = mat_vec_mul(AT, y)
    for i in range(k):
        u[i] = poly_add(u[i], e1[i])
    mu = decompress(byte_decode(m, 1), 1)
    v = (vec_dot(t, y) + e2 + mu) % q
    c1 = b''.join(byte_encode(compress(u[i], du), du) for i in range(k))
    c2 = byte_encode(compress(v, dv), dv)
    return c1 + c2

def decrypt(dpke, c):
    c1 = c[0: 32 * du * k]
    c2 = c[32 * du * k: 32 * (k * du + dv)]

    u = [decompress(byte_decode(c1[i * 32 * du: (i + 1) * 32 * du], du), du) for i in range(k)] 
    v = decompress(byte_decode(c2, dv), dv)
    s = [  byte_decode( dpke[i * 384: (i+1) * 384] , 12)     for i in range (k)]

    w = (v - vec_dot(u, s) ) % q
    m = byte_encode(compress(w, 1), 1)

    return m 

def key_gen_internal(d, z):
    epke, dpke = key_gen(d)
    dk = dpke  + epke + hashlib.sha3_256(epke).digest() + z
    return epke, dk

def encaps_internal(ek , m):
    g = hashlib.sha3_512(m + hashlib.sha3_256(ek).digest()).digest()
    K, r = g[:32], g[32:]
    c = encrypt(ek, m, r)
    return K, c

def decaps_internal(dk, c):
    dpke = dk[0 : 384 * k]
    epke = dk[384 * k : 768 * k + 32]
    h = dk[768 * k + 32 : 768 * k + 64]
    z = dk[768 * k + 64 : 768 * k + 96]
    mprime = decrypt(dpke, c)
    g = hashlib.sha3_512(mprime + h).digest()
    Kprime, rprime = g[:32], g[32:]
    K = hashlib.shake_256(z + c).digest(32)
    cprime = encrypt(epke, mprime, rprime)
    if c != cprime:
        Kprime = K
    return Kprime

def ml_kem_key_gen():
    d = secrets.token_bytes(32)
    z = secrets.token_bytes(32)
    ek, dk = key_gen_internal(d, z)
    return ek, dk


def encaps(ek):
    m = secrets.token_bytes(32)
    K, c = encaps_internal(ek, m)
    return K, c

def decaps(dk, c):
    Kprime = decaps_internal(dk, c)
    return Kprime

def main():
    ek, dk = ml_kem_key_gen()
    print (f"ek: {len(ek)} bytes \n dk: {len(dk)} bytes")

    K_a, c = encaps(ek)
    K_b = decaps(dk, c)

    print (f"K_a: {len(K_a)} bytes \n K_b: {len(K_b)} bytes")
    print (f"Ciphertext: {len(c)} bytes \n assert: {K_a == K_b}")
    assert K_a == K_b

if __name__ == "__main__":
    main()