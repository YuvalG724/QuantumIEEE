# this file demonstrates a simple rsa encryption and decryption.
# it also shows two classical (non-quantum) attacks to find the private key:
# brute-force and pollard's rho algorithm.
# this is to compare their performance with a quantum attack.
#just a simple RSA encryption and decryption example
# thought it would be good to show how the attacks work
import time
import math

# the message to be encrypted. 'b' before the string means it's a byte string.
message = b"I"

# rsa works with numbers, so we convert the message from bytes to an integer.
message_int = int.from_bytes(message, byteorder='big')
print("Message as integer:", message_int)

# we choose two prime numbers, p and q. in a real scenario, these would be very large.
p = 17
q = 23
# n is the modulus for the public and private keys.
n = p * q  # n = 391
# phi(n) is euler's totient function. it's used to find the private key.
phi = (p - 1) * (q - 1)  # phi = 352
# e is the public key exponent. it must be a number that is not a factor of phi.
e = 3  # Choose small e such that gcd(e, phi) = 1

# the message is encrypted using the public key (e, n).
# this is done by calculating (message ^ e) mod n.
encrypted_message = pow(message_int, e, n)
print("Encrypted Message:", encrypted_message)

# this is a simple attack that tries to find the factors of n by checking every number from 2 up to n.
def brute_force(n):
    for i in range(2, n):
        if n % i == 0:
            return i, n // i
    return None, None

# pollard's rho is a more efficient algorithm for finding prime factors than brute-force.
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

# this function calculates the modular multiplicative inverse of a number 'a' modulo 'm'.
# it's used to find the private key 'd' from the public key 'e' and phi.
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

# this function decrypts the message using the private key (d, n).
# it calculates (ciphertext ^ d) mod n.
def decrypt(cipher_int, d, n):
    plain_int = pow(cipher_int, d, n)
    try:
        return plain_int.to_bytes((plain_int.bit_length() + 7) // 8, byteorder='big').decode()
    except:
        return "<decode error>"

# here we simulate the brute-force attack.
# we find the factors p and q, then calculate phi, then the private key d.
# finally, we decrypt the message and measure the time it took.
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

# here we simulate the pollard's rho attack, which is generally faster.
# we do the same steps as with brute-force to find the private key and decrypt the message.
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
