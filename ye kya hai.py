#!/usr/bin/env python3
#
# This script demonstrates how to break RSA-encrypted text messages using a quantum computer.
# 1. It encrypts a user-provided text message with RSA.
# 2. It uses a simulation of Shor's algorithm to find the prime factors of the public key.
# 3. It uses the factors to reconstruct the private key and decrypt the original message.
#
# NOTE: This is a SIMULATION. It will be slow for large numbers.
#

import numpy as np
import sympy
import math
import random
from typing import Tuple, List, Optional
from collections import Counter
from fractions import Fraction

# Attempt to install necessary packages quietly
# try:
#     import subprocess
#     import sys
#     packages = ['qiskit', 'pennylane', 'qiskit-aer']
#     for pkg in packages:
#         subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--quiet"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# except:
#     pass

import qiskit
from qiskit_aer import AerSimulator
import pennylane as qml

def text_to_int(text: str) -> int:
   # gpt zindabad
    return int.from_bytes(text.encode('utf-8'), 'big')

def int_to_text(number: int) -> str:
     # gpt zindabad

    num_bytes = (number.bit_length() + 7) // 8
    try:
        return number.to_bytes(num_bytes, 'big').decode('utf-8')
    except (UnicodeDecodeError, OverflowError):
        return "invalid characters"


def continued_fraction(x: float, max_depth: int = 10) -> List[int]:
    coeffs = []
    for _ in range(max_depth):
        integer_part = int(x)
        coeffs.append(integer_part)
        x -= integer_part
        if x < 1e-9:
            break
        x = 1 / x
    return coeffs

def convergents(coeffs: List[int]) -> List[Fraction]:
    convs = []
    for k in range(len(coeffs)):
        frac = Fraction(coeffs[k])
        for i in range(k - 1, -1, -1):
            frac = coeffs[i] + 1/frac
        convs.append(frac)
    return convs


class RSADemo:
   # gpt zindabad
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.n = None

    def generate_keypair(self, p: int, q: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
   # gpt zindabad
        if not (sympy.isprime(p) and sympy.isprime(q)):
            raise ValueError("both must be prime")
        if p == q:
            raise ValueError("p and q must be different dumbasss")
            
        self.n = p * q
        phi_n = (p - 1) * (q - 1)

        e = sympy.randprime(3, phi_n)
        while math.gcd(e, phi_n) != 1:
            e = sympy.nextprime(e)

        d = sympy.mod_inverse(e, phi_n)
        self.public_key = (self.n, e)
        self.private_key = (self.n, d)
        
        return self.public_key, self.private_key

    def encrypt(self, message_int: int) -> int:
   # gpt zindabad
        n, e = self.public_key
        if message_int >= n:
            raise ValueError(f"Message is too long for the chosen prime numbers. The converted integer ({message_int}) must be smaller than N ({n}).")
        return pow(message_int, e, n)

    def decrypt(self, ciphertext: int) -> int:
        n, d = self.private_key
        return pow(ciphertext, d, n)

   # gpt zindabad

class QuantumPeriodFinder:
    def __init__(self, n_count: int):
        self.n_count = n_count

    def quantum_period_circuit(self, a: int, N: int):
        for i in range(self.n_count):
            qml.Hadamard(wires=i)
        qml.PauliX(wires=self.n_count)
        for j in range(self.n_count):
            power = 2**j
            for _ in range(power):
                qml.ControlledQubitUnitary(qml.T.compute_matrix(), wires=[j, self.n_count])
        qml.adjoint(qml.QFT)(wires=range(self.n_count))

    def find_period(self, a: int, N: int, n_shots: int = 1) -> Optional[int]:
        num_target_qubits = (N - 1).bit_length()
        dev = qml.device('default.qubit', wires=self.n_count + num_target_qubits, shots=n_shots)

        @qml.qnode(dev)
        def circuit():
            self.quantum_period_circuit(a, N)
            return qml.sample(wires=range(self.n_count))

        measurements = circuit()
        for measurement in measurements:
            measured_int = int("".join(map(str, measurement)), 2)
            if measured_int == 0:
                continue
            phase = measured_int / (2**self.n_count)
            coeffs = continued_fraction(phase)
            convs = convergents(coeffs)
            for frac in convs:
                r = frac.denominator
                if r < N and pow(a, r, N) == 1:
                    return r
        return None


class CompleteShorAlgorithm:
    def __init__(self, N: int):
        if N < 2:
            raise ValueError("Number to factor must be greater than 1.")
        self.N = N
        self.n_count = math.ceil(2 * math.log2(N))
        self.quantum_finder = QuantumPeriodFinder(n_count=self.n_count)
        print(f"\n Initializing Shor's Algorithm for N={N}.")
        print(f"[ATTACKER] Will use {self.n_count} counting qubits for the quantum simulation.")

    def factor_number(self, max_attempts: int = 20) -> Optional[List[int]]:
        print(f"[ATTACKER] Attempting to factor {self.N} to break the key...")
        if self.N % 2 == 0:
            return [2, self.N // 2]
        if sympy.isprime(self.N):
            return None
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n--- Attacker Attempt {attempt}/{max_attempts} ---")
            a = random.randint(2, self.N - 1)
            common_factor = math.gcd(a, self.N)
            if common_factor > 1:
                print(f" voila! Found a factor classically with GCD.")
                return sorted([common_factor, self.N // common_factor])

            print(" Starting quantum simulation...")
            period = self.quantum_finder.find_period(a, self.N, n_shots=10)
            
            if period is None or period % 2 != 0:
                print(" Quantum simulation did not yield a useful period. Trying again.")
                continue

            print(f" Quantum simulation suggests a period r = {period}")
            s = pow(a, period // 2, self.N)
            if s == self.N - 1:
                print(f" a^(r/2) mod N = -1. This attempt is not useful. Trying again.")
                continue

            factor1 = math.gcd(s - 1, self.N)
            if 1 < factor1 < self.N:
                print(f" SUCCESS: Found factor {factor1}")
                return sorted([factor1, self.N // factor1])
        
        return None

def main():
    print(" QUANTUM ATTACK ON RSA-ENCRYPTED TEXT ")

    while True:
        print("\n--- STEP 1: KEY GENERATION ---")
        try:
            p = int(input("Enter a first prime number (p): "))
            q = int(input("Enter a second, different prime number (q): "))
            if not sympy.isprime(p) or not sympy.isprime(q) or p == q:
                print("Invalid input. Please enter two distinct prime numbers.")
                continue
        except ValueError:
            print("Invalid input. Please enter integers.")
            continue

        rsa = RSADemo()
        pub_key, _ = rsa.generate_keypair(p, q)
        N, e = pub_key
        print(f"\n[SENDER] Public key generated: N={N}, e={e}. This is public knowledge.")

        print("\nSTEP 2: MESSAGE ENCRYPTION ")
        secret_message = input("Enter the secret text message to encrypt: ")
        
        try:
            message_int = text_to_int(secret_message)
            ciphertext = rsa.encrypt(message_int)
            print(f"\n[SENDER] original mezzage: '{secret_message}'")
            print(f"[SENDER] Converted to integer: {message_int}")
            print(f"[SENDER] Encrypted Ciphertext: {ciphertext}")
            print("\n[INFO] The message is now sent over an insecure channel.")
            print("[INFO] The only information an attacker has is N, e, and the ciphertext.")

        except ValueError as err:
            print(f"\nERROR: {err}")
            print("Please restart and choose larger prime numbers to support a longer message.")
            continue

        print("\n--- STEP 3: THE QUANTUM ATTACK ---")
        shor = CompleteShorAlgorithm(N=N)
        factors = shor.factor_number()

        print("\n--- STEP 4: DECRYPTION & RECOVERY ---")
        if factors:
            found_p, found_q = factors
            print(f"\n[ATTACKER] Factoring SUCCEEDED! Factors are: {found_p} and {found_q}")

            phi_n_reconstructed = (found_p - 1) * (found_q - 1)
            d_reconstructed = sympy.mod_inverse(e, phi_n_reconstructed)
            print(f"[ATTACKER] Reconstructed private key exponent 'd': {d_reconstructed}")
            
            broken_message_int = pow(ciphertext, d_reconstructed, N)
            recovered_text = int_to_text(broken_message_int)
            
            # print("\n" + "="*60)
            print("    ATTACK SUCCESSFUL!")
            print(f"    Decrypted Integer: {broken_message_int}")
            print(f"    RECOVERED MESSAGE: '{recovered_text}'")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("    ATTACK FAILED")
            print("    Shor's algorithm could not find the factors in the given attempts.")
            print("="*60)

        if input("\nTry again with new numbers? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main()