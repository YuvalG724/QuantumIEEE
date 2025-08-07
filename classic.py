#just a simple RSA encryption and decryption example
# thought it would be good to show how the attacks work
import time
import math

message = b"I"

message_int = int.from_bytes(message, byteorder='big')
print("Message as integer:", message_int)

p = 17
q = 23
n = p * q  # n = 391
phi = (p - 1) * (q - 1)  # phi = 352
e = 3  # Choose small e such that gcd(e, phi) = 1

encrypted_message = pow(message_int, e, n)
print("Encrypted Message:", encrypted_message)

def brute_force(n):
    for i in range(2, n):
        if n % i == 0:
            return i, n // i
    return None, None

def pollards_rho(n):
    if n % 2 == 0:
        return 2, n // 2
    def f(x): return (x * x + 1) % n
    x, y, d = 2, 2, 1
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = math.gcd(abs(x - y), n)
    if d == n:
        return None, None
    return d, n // d

def modinv(a, m):
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        else:
            g, y, x = egcd(b % a, a)
            return g, x - (b // a) * y, y
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("modular inverse does not exist")
    return x % m

def decrypt(cipher_int, d, n):
    plain_int = pow(cipher_int, d, n)
    try:
        return plain_int.to_bytes((plain_int.bit_length() + 7) // 8, byteorder='big').decode()
    except:
        return "<decode error>"

start = time.time()
p_b, q_b = brute_force(n)
phi_b = (p_b - 1) * (q_b - 1)
d_b = modinv(e, phi_b)
decrypted_b = decrypt(encrypted_message, d_b, n)
end = time.time()
elapsed = end-start
print("\n[Brute Force]")
print("Factors: p =", p_b, ", q =", q_b)
print("Private Key (d):", d_b)
print("Decrypted Message:", decrypted_b)
print(f"Time Taken:{elapsed:.6f} seconds")

start = time.time()
p_p, q_p = pollards_rho(n)
phi_p = (p_p - 1) * (q_p - 1)
d_p = modinv(e, phi_p)
decrypted_p = decrypt(encrypted_message, d_p, n)
end = time.time()

print("\n[Pollard's Rho]")
print("Factors: p =", p_p, ", q =", q_p)
print("Private Key (d):", d_p)
print("Decrypted Message:", decrypted_p)
print(f"Time Taken:{elapsed:.6f}seconds")
