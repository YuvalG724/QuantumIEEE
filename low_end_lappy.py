#!/usr/bin/env python3
import math
import random
from typing import Tuple, List, Optional
from fractions import Fraction

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def get_next_prime(n: int) -> int:
    while not is_prime(n):
        n += 1
    return n

def mod_inverse(a: int, m: int) -> int:
    if math.gcd(a, m) != 1:
        raise ValueError("Modular inverse does not exist")
    
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def text_to_int(text: str) -> int:
    return int.from_bytes(text.encode('utf-8'), 'big')

def int_to_text(number: int) -> str:
    if number <= 0:
        return ""
    
    num_bytes = (number.bit_length() + 7) // 8
    try:
        return number.to_bytes(num_bytes, 'big').decode('utf-8')
    except (UnicodeDecodeError, OverflowError):
        return "[Invalid characters]"

class SimpleRSA:
    
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.n = None
        self.p = None
        self.q = None

    def generate_keypair(self, p: int, q: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        if not (is_prime(p) and is_prime(q)):
            raise ValueError("Both numbers must be prime")
        if p == q:
            raise ValueError("p and q must be different")
            
        self.p = p
        self.q = q
        self.n = p * q
        phi_n = (p - 1) * (q - 1)

        e = 65537
        if e >= phi_n:
            e = 3
        while math.gcd(e, phi_n) != 1:
            e = get_next_prime(e + 1)

        d = mod_inverse(e, phi_n)
        self.public_key = (self.n, e)
        self.private_key = (self.n, d)
        
        return self.public_key, self.private_key

    def encrypt(self, message_int: int) -> int:
        n, e = self.public_key
        if message_int >= n:
            raise ValueError(f"Message too large. Integer {message_int} must be < {n}")
        return pow(message_int, e, n)

    def decrypt(self, ciphertext: int) -> int:
        n, d = self.private_key
        return pow(ciphertext, d, n)

class ClassicalFactorizer:
    
    def __init__(self, n: int):
        self.n = n
        print(f"\n[ATTACKER] Attempting to factor N = {n}")

    def trial_division(self, limit: Optional[int] = None) -> Optional[Tuple[int, int]]:
        if limit is None:
            limit = min(10000, int(math.sqrt(self.n)) + 1)
        
        print(f"[ATTACKER] Trying trial division up to {limit}...")
        
        if self.n % 2 == 0:
            return (2, self.n // 2)
        
        for i in range(3, limit, 2):
            if self.n % i == 0:
                print(f"[ATTACKER] Found factor: {i}")
                return (i, self.n // i)
        
        print(f" Trial division failed (tried up to {limit})")
        return None

    def pollards_rho(self, max_iterations: int = 10000) -> Optional[Tuple[int, int]]:
        print(f" tryingusing rho's algo")
        
        if self.n % 2 == 0:
            return (2, self.n // 2)
        
        def f(x):
            return (x * x + 1) % self.n
        
        x = random.randint(2, self.n - 1)
        y = x
        d = 1
        
        iterations = 0
        while d == 1 and iterations < max_iterations:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), self.n)
            iterations += 1
        
        if d != 1 and d != self.n:
            print(f" factor with rho's {d}")
            return (d, self.n // d)
        
        print(" Pollard's Rho failed")
        return None

    def simulated_quantum_factor(self) -> Optional[Tuple[int, int]]:
      
        print(" Simulating quantum factoring (Shor's algorithm)...")
        print(" Note: This is a classical simulation for demonstration")
        
      
        result = self.pollards_rho(max_iterations=50000)
        if result:
            print("Quantum simulation successful!")
            return result
        
        print(" Quantum simulation: trying extended search...")
        result = self.trial_division(limit=50000)
        if result:
            print(" Quantum simulation successful!")
            return result
        
        print(" Quantum simulation failed - number may be too large")
        return None

def main():
    print("   RSA ENCRYPTION & DEMO")
    print("   (Simplified for Educational Purposes)")

    while True:
        
        print("enter small primes for demonstration (e.g., 61, 53, 47, 41, 37, 31)")
        
        try:
            p = int(input(" first prime (p): "))
            q = int(input(" second prime (q): "))
            
            if not is_prime(p) or not is_prime(q):
                print("Error: Both numbers must be prime!")
                continue
            if p == q:
                print("Error: p and q must be different!")
                continue
            if p * q < 256:  
                print("Warning: Very small primes - message will be limited to single characters")
                
        except ValueError:
            print("Error: Please enter valid integers")
            continue

        rsa = SimpleRSA()
        try:
            pub_key, priv_key = rsa.generate_keypair(p, q)
            n, e = pub_key
            print(f"\nkey generation Success!")
            print(f"Public Key:  N = {n}, e = {e}")
            print(f"Private Key: d = {priv_key[1]} (kept secret)")
            
        except Exception as err:
            print(f"Error generating keys: {err}")
            continue

        print("\n mezzage encryption")
        message = input("Enter message to encrypt: ")
        
        try:
            message_int = text_to_int(message)
            print(f"Message as integer: {message_int}")
            
            if message_int >= n:
                print(f"Error: Message too long for key size!")
                print(f"Try shorter message or larger primes")
                continue
                
            ciphertext = rsa.encrypt(message_int)
            print(f"\nOriginal: '{message}'")
            print(f" Encrypted: {ciphertext}")
            print(f" Message sent over insecure channel...")
            
        except Exception as err:
            print(f"Encryption error: {err}")
            continue

        # THE attack
        print("\n ATTACK ")
        print("[INFO] Attacker knows: N, e, and ciphertext")
        print("[INFO] Attacker needs to factor N to find private key")
        
        factorizer = ClassicalFactorizer(n)
        
        factors = None
        
        factors = factorizer.trial_division()
        
        if not factors:
            factors = factorizer.pollards_rho()
        if not factors:
            factors = factorizer.simulated_quantum_factor()

        print("\n DECRYPTION ")
        if factors:
            found_p, found_q = factors
            print(f"\n Factors found: {found_p} × {found_q} = {n}")
            
            # Reconstruct private key
            phi_n = (found_p - 1) * (found_q - 1)
            try:
                d_recovered = mod_inverse(e, phi_n)
                print(f" Recovered private key: d = {d_recovered}")
                
                # Decrypt the message
                decrypted_int = pow(ciphertext, d_recovered, n)
                decrypted_text = int_to_text(decrypted_int)
                
                print("\n" + "=" * 50)
                print("    ATTACK IS A SUCCESS")
                print(f"   Original message: '{message}'")
                print(f"   Recovered message: '{decrypted_text}'")
                print("OYE BALLE BALLE!!!!!!!!!!!!!!!!!!!")
                
            except Exception as err:
                print(f"Error in key reconstruction: {err}")
        else:
            print("\n" + "=" * 50)
            print("    ATTACK FAILED")
            print("   Try smaller primes to see successful attack")

        if input("\nTry again? (y/n): ").lower() != 'y':
            break

  

if __name__ == "__main__":
    main()