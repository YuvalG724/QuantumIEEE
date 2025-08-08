# this file shows how quantum computing can be used to break rsa encryption.
# however, the code is not fully functional due to issues with quantum libraries.
#tried to show how quantum is better but can't get it to work
#issue with the libs required for quantum computing
import time
import random
import math
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import  hashes

# generate an rsa key pair. the public key will be used for encryption,
# and the private key for decryption.
recipient_private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
recipient_public_key = recipient_private_key.public_key()

# this is the message to be encrypted.
message = b"Hi"

# the message is encrypted using the recipient's public key.
# oaep padding is used for additional security.
encrypted_message = recipient_public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()), 
        algorithm=hashes.SHA256(),                    
        label=None
    )
)

# the encrypted message is printed. we only show the first 60 bytes for brevity.
print("Encrypted Message (bytes):", encrypted_message[:60], "...")

# the message is decrypted using the recipient's private key.
decrypted_message = recipient_private_key.decrypt(
    encrypted_message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print("Decrypted Message:", decrypted_message.decode())

# the public numbers (e and n) are extracted from the public key.
# these are the values that an attacker would know.
publicNumbers = recipient_public_key.public_numbers()
e = publicNumbers.e
n = publicNumbers.n
print("Public Key (e, n):", (e, n))

# this is a simple attack that tries to find the factors of n by checking every number from 2 up to n.
def bruteForce(n):
    for i in range(2,n):
        if n % i == 0:
            return [i,n//i]
    return []

# pollard's rho is a more efficient algorithm for finding prime factors than brute-force.
def pollards(n):
    if n%2 == 0:
        return [2, n // 2]
    def f(x):
        return (x * x + 1) % n
    x,y,d = 2, 2, 1
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = math.gcd(abs(x - y), n)
    if d == n:
        return []
    return [d, n // d]

# this function calculates the modular multiplicative inverse of a number 'a' modulo 'm'.
# it's used to find the private key 'd' from the public key 'e' and phi.
def modinv(a, m):
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        else:
            g,y,x = egcd(b%a,a)
            return g, x - (b // a) * y, y
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m
    
# this function decrypts the message using the private key (d, n).
# it calculates (ciphertext ^ d) mod n.
def decrypt(encrypted_message, d, n):
    cipherInt = int.from_bytes(encrypted_message, byteorder='big')
    plainTextInt = pow(cipherInt, d, n)
    return plainTextInt.to_bytes((plainTextInt.bit_length() + 7) // 8, byteorder='big')

# here we simulate the brute-force attack.
# we find the factors p and q, then calculate phi, then the private key d.
# finally, we decrypt the message and measure the time it took.
start = time.time()
p,q = bruteForce(n)
phi = (p - 1) * (q - 1)
d_brute = modinv(e, phi)
end = time.time()
print("Brute Force Time:", end - start, "seconds")
decrypted_message_brute = decrypt(encrypted_message, d_brute, n)
print("Decrypted Message (Brute Force):", decrypted_message_brute.decode())

# here we simulate the pollard's rho attack, which is generally faster.
# we do the same steps as with brute-force to find the private key and decrypt the message.
start = time.time()
p1, q1 = pollards(n)
phi1 = (p1 - 1) * (q1 - 1)
d_pollard = modinv(e, phi1)
end = time.time()
print("Pollard's Time:", end - start, "seconds")
decrypted_message_pollard = decrypt(encrypted_message, d_pollard, n)
print("Decrypted Message (Pollard's):", decrypted_message_pollard.decode())

cipherInt = int.from_bytes(encrypted_message, byteorder='big')
plainText_brute = pow(cipherInt, d_brute, n)
plainText_pollard = pow(cipherInt, d_pollard, n)
plainText_brute = plainText_brute.to_bytes((plainText_brute.bit_length() + 7) // 8, byteorder='big')
plainText_pollard = plainText_pollard.to_bytes((plainText_pollard.bit_length() + 7) // 8, byteorder='big')

print("Decrypted Message (Brute Force):", plainText_brute.decode())
print("Decrypted Message (Pollard's):", plainText_pollard.decode())