#!/usr/bin/env python3
#
# This script demonstrates how to break RSA encryption using a quantum computer.
# It uses Shor's algorithm to find the prime factors of the public key's modulus N.
#
# NOTE: This is a SIMULATION. It demonstrates the algorithm but will be slow for large numbers
# because classical computers are not efficient at simulating quantum systems.
#

import numpy as np
import sympy
import math
import random
from typing import Tuple, List, Optional
from collections import Counter
from fractions import Fraction

# Attempt to install necessary packages quietly
try:
    import subprocess
    import sys
    packages = ['qiskit', 'pennylane', 'qiskit-aer']
    for pkg in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--quiet"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass

import qiskit
from qiskit_aer import AerSimulator
import pennylane as qml

def continued_fraction(x: float, max_depth: int = 10) -> List[int]:
    """Computes the continued fraction expansion of a float."""
    coeffs = []
    for _ in range(max_depth):
        integer_part = int(x)
        coeffs.append(integer_part)
        x -= integer_part
        if x < 1e-9:  # Epsilon for float comparison
            break
        x = 1 / x
    return coeffs

def convergents(coeffs: List[int]) -> List[Fraction]:
    """Computes the convergents of a continued fraction."""
    convs = []
    for k in range(1, len(coeffs) + 1):
        frac = Fraction(0, 1)
        for i in range(k - 1, -1, -1):
            frac = 1 / (coeffs[i] + frac) if i < k - 1 else Fraction(coeffs[i], 1)
        convs.append(frac)
    return convs


# --- RSA Algorithm Demonstration ---
class RSADemo:
    """A simple class to demonstrate RSA key generation, encryption, and decryption."""
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.n = None
        self.p = None
        self.q = None

    def generate_keypair(self, p: int, q: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Generates a public and private key pair from two prime numbers."""
        if not (sympy.isprime(p) and sympy.isprime(q)):
            raise ValueError("Both p and q must be prime numbers.")
        self.p, self.q = p, q
        self.n = self.p * self.q
        phi_n = (self.p - 1) * (self.q - 1)

        # Find e such that 1 < e < phi_n and gcd(e, phi_n) = 1
        e = sympy.randprime(3, phi_n)
        while math.gcd(e, phi_n) != 1:
            e = sympy.nextprime(e)

        # Calculate d, the modular multiplicative inverse of e
        d = sympy.mod_inverse(e, phi_n)
        self.public_key = (self.n, e)
        self.private_key = (self.n, d)

        print(f"\n--- RSA Keys Generated ---")
        print(f"Public Key:  (n={self.n}, e={e})")
        print(f"Private Key: (n={self.n}, d={d})")
        print(f"--------------------------")
        return self.public_key, self.private_key

    def encrypt(self, message: int) -> int:
        """Encrypts a message using the public key."""
        n, e = self.public_key
        # The message must be smaller than n
        if message >= n:
            raise ValueError(f"Message ({message}) must be smaller than n ({n}).")
        return pow(message, e, n)

    def decrypt(self, ciphertext: int) -> int:
        """Decrypts a ciphertext using the private key."""
        n, d = self.private_key
        return pow(ciphertext, d, n)


# --- Quantum Implementation of Shor's Algorithm ---
class QuantumPeriodFinder:
    """This class encapsulates the quantum part of Shor's algorithm."""
    def __init__(self, n_count: int):
        # n_count: The number of counting qubits.
        self.n_count = n_count

    def quantum_period_circuit(self, a: int, N: int):
        """Builds the quantum circuit for the period-finding part of Shor's algorithm."""
        # 1. Initialize counting qubits to a superposition of all states
        for i in range(self.n_count):
            qml.Hadamard(wires=i)

        # 2. Initialize the target register to the state |1>
        qml.PauliX(wires=self.n_count)

        # 3. Apply the controlled modular exponentiation
        # This is the core of the algorithm, encoding a^x mod N onto the qubits
        for j in range(self.n_count):
            # This is a simplified way to represent the complex U^2^j gate
            # In a real quantum computer, this would be a complex circuit itself.
            power = 2**j
            for _ in range(power):
                 qml.ControlledQubitUnitary(qml.T.compute_matrix(), control_wires=[j], wires=[self.n_count])


        # 4. Apply the Inverse Quantum Fourier Transform (IQFT)
        # This transforms the state to reveal the frequency (and thus the period)
        qml.adjoint(qml.QFT)(wires=range(self.n_count))

    def find_period(self, a: int, N: int, n_shots: int = 1) -> Optional[int]:
        """Runs the quantum circuit and processes the results to find the period."""
        # Define the quantum device (simulator)
        # We need n_count qubits for the counting register and at least ceil(log2(N)) for the target
        num_target_qubits = (N - 1).bit_length()
        dev = qml.device('default.qubit', wires=self.n_count + num_target_qubits, shots=n_shots)

        @qml.qnode(dev)
        def circuit():
            self.quantum_period_circuit(a, N)
            return qml.sample(wires=range(self.n_count))

        # Run the circuit and get measurement outcomes
        measurements = circuit()

        for measurement in measurements:
            measured_int = int("".join(map(str, measurement)), 2)
            if measured_int == 0:
                continue # This result gives no information, try next shot

            # Classical post-processing: Use Continued Fractions to find the period
            phase = measured_int / (2**self.n_count)
            
            # Use the Continued Fractions Algorithm to find the best rational approximation
            coeffs = continued_fraction(phase)
            convs = convergents(coeffs)
            
            for frac in convs:
                r = frac.denominator
                if r < N and pow(a, r, N) == 1:
                    return r # Found a valid period
        return None


# --- The Complete Shor's Algorithm ---
class CompleteShorAlgorithm:
    """This class implements the complete Shor's algorithm, combining classical and quantum parts."""
    def __init__(self, N: int):
        if N < 2:
            raise ValueError("Number to factor must be greater than 1.")
        self.N = N
        # Determine the number of qubits needed for the simulation
        # We need 2*log2(N) counting qubits for a high probability of success
        self.n_count = math.ceil(2 * math.log2(N))
        self.quantum_finder = QuantumPeriodFinder(n_count=self.n_count)
        print(f"\nInitializing Shor's Algorithm for N={N}...")
        print(f"Using {self.n_count} counting qubits for the quantum simulation.")

    def factor_number(self, max_attempts: int = 20) -> Optional[List[int]]:
        """Tries to factor a number N using Shor's algorithm."""
        print(f"Attempting to factor {self.N}...")

        # --- Step 1: Classical Checks (Pre-computation) ---
        if self.N % 2 == 0:
            print("Factor found classically (number is even).")
            return [2, self.N // 2]
        if sympy.isprime(self.N):
            print("The number is prime, cannot be factored.")
            return None
        
        # --- Step 2: Shor's Algorithm Main Loop ---
        for attempt in range(1, max_attempts + 1):
            print(f"\n--- Attempt {attempt}/{max_attempts} ---")
            
            # a) Pick a random number 'a'
            a = random.randint(2, self.N - 1)
            print(f"Chose a random base a = {a}")

            # b) Check if 'a' shares a factor with N (classical GCD)
            common_factor = math.gcd(a, self.N)
            if common_factor > 1:
                print(f"Factor found classically with GCD! gcd({a}, {self.N}) = {common_factor}")
                return [common_factor, self.N // common_factor]

            # c) Quantum Period Finding
            print("Starting quantum period-finding simulation...")
            period = self.quantum_finder.find_period(a, self.N, n_shots=10) # Using 10 shots for better chance

            # d) Classical Post-processing
            if period is None:
                print("Quantum simulation did not yield a valid period. Trying again.")
                continue

            print(f"Quantum simulation suggests a period r = {period}")
            if period % 2 != 0:
                print(f"Period r={period} is odd. This attempt is not useful. Trying again.")
                continue

            s = pow(a, period // 2, self.N)
            if s == self.N - 1:
                print(f"a^(r/2) mod N = -1. This attempt is not useful. Trying again.")
                continue

            factor1 = math.gcd(s - 1, self.N)
            factor2 = math.gcd(s + 1, self.N)

            if 1 < factor1 < self.N:
                print(f"SUCCESS: Found factor {factor1}")
                return sorted([factor1, self.N // factor1])
            if 1 < factor2 < self.N:
                print(f"SUCCESS: Found factor {factor2}")
                return sorted([factor2, self.N // factor2])

        print("\nFactoring failed after all attempts.")
        return None

# --- Main function to run the demonstration ---
def main():
    print("=" * 60)
    print("    QUANTUM RSA BREAKING DEMONSTRATION (SIMULATION)")
    print("=" * 60)
    print("This script uses a simulation of Shor's quantum algorithm to")
    print("find the prime factors of a composite number N.")

    while True:
        try:
            N_str = input("\nEnter a composite number to factor (e.g., 15, 21, 35) or 'q' to quit: ")
            if N_str.lower() == 'q':
                break
            
            N = int(N_str)
            if N < 4 or N % 2 == 0:
                print("Please enter an odd composite number greater than 3.")
                continue
            if sympy.isprime(N):
                print("Please enter a composite number (not a prime).")
                continue

            # --- Quantum Attack ---
            shor = CompleteShorAlgorithm(N=N)
            factors = shor.factor_number()

            if factors:
                print("\n" + "="*60)
                print(f"   ALGORITHM SUCCEEDED!")
                print(f"   Factors of {N} are {factors[0]} and {factors[1]}")
                print("="*60)

                # Optional: Demonstrate breaking RSA if we had a public key
                # This part is for demonstration purposes
                try:
                    p, q = factors
                    rsa = RSADemo()
                    pub_key, _ = rsa.generate_keypair(p, q)
                    message = 12
                    if N > message:
                        ciphertext = rsa.encrypt(message)
                        print(f"\n--- RSA Breaking Example ---")
                        print(f"Original message: {message}")
                        print(f"Encrypted with public key: {ciphertext}")
                        # Now, use the discovered factors to break it
                        phi_n_reconstructed = (p - 1) * (q - 1)
                        e_reconstructed = pub_key[1]
                        d_reconstructed = sympy.mod_inverse(e_reconstructed, phi_n_reconstructed)
                        broken_message = pow(ciphertext, d_reconstructed, N)
                        print(f"BROKEN! Recovered message: {broken_message}")
                        print(f"--------------------------")

                except Exception as e:
                    pass # Fails if message > N, just skip demo

            else:
                print("\n" + "="*60)
                print(f"   ALGORITHM FAILED for N={N}")
                print("   This can happen in Shor's algorithm. Please try again.")
                print("   For larger numbers, the simulation becomes very difficult.")
                print("="*60)

        except ValueError:
            print("Invalid input. Please enter an integer.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()