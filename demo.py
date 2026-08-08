import hashlib
import secrets
import hmac
import sys

from MLKEM import ( 
    ml_kem_key_gen,
    encaps,
    decaps,
    encaps_internal,
    decaps_internal,
    key_gen_internal,
    k,
    du,
    dv,
)

def hx(b, count=16):
    s = b[:count].hex()
    return s + ("..." if len(b) > count else "")

def derive(K, label):
    return hashlib.shake_256(K + label).digest(32)

def dem_encrypt(K, plaintext: bytes):
    nonce = secrets.token_bytes(16)
    enc_key = derive(K, b"enc" + nonce)
    mac_key = derive(K, b"mac" + nonce)
    keystream = hashlib.shake_256(enc_key).digest(len(plaintext))
    ct = bytes(a ^ b for a, b in zip(plaintext, keystream))
    tag = hmac.new(mac_key, nonce + ct, hashlib.sha256).digest()
    return nonce + ct + tag

def dem_decrypt(K, blob: bytes):
    nonce, ct, tag = blob[:16], blob[16:-32], blob[-32:]
    enc_key = derive(K, b"enc" + nonce)
    mac_key = derive(K, b"mac" + nonce)
    expected_tag = hmac.new(mac_key, nonce + ct, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("Invalid tag")
    keystream = hashlib.shake_256(enc_key).digest(len(ct))
    plaintext = bytes(a ^ b for a, b in zip(ct, keystream))
    return plaintext

def main():
    message = input("Enter a message to encrypt: ")
    data = message.encode("utf-8")
    print(f"message      : {message!r} ({len(data)} bytes)\n")

    print("[1] Bob generates a keypair")
    ek, dk = ml_kem_key_gen()
    print(f"    ek  {len(ek)} bytes  {hx(ek)}")
    print(f"    dk  {len(dk)} bytes  {hx(dk)}\n")

    print("[2] Alice encapsulates against Bob's ek")
    K_a, c = encaps(ek)
    print(f"    K   {len(K_a)} bytes  {K_a.hex()}")
    print(f"    c   {len(c)} bytes  {hx(c)}\n")

    print("[3] Alice encrypts the message under K")
    blob = dem_encrypt(K_a, data)
    print(f"    blob {len(blob)} bytes  {hx(blob, 24)}")
    print(f"    wire total: {len(c) + len(blob)} bytes\n")

    print("[4] Bob decapsulates")
    K_b = decaps(dk, c)
    print(f"    K   {K_b.hex()}")
    print(f"    keys agree: {K_a == K_b}\n")

    print("[5] Bob decrypts")
    out = dem_decrypt(K_b, blob)
    print(f"    recovered: {out.decode('utf-8')!r}")
    print(f"    round trip ok: {out == data}\n")

 


if __name__ == "__main__":
    main()