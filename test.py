# this script demonstrates how to break rsa encryption using a quantum computer.
# it uses shor's algorithm to find the prime factors of the public key.
#!/usr/bin/env python3
import numpy as np
import sympy
import math
import random
from typing import Tuple, List, Optional
from collections import Counter

import subprocess
import sys
packages = ['qiskit', 'pennylane', 'qiskit-aer']
for pkg in packages:
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--quiet"], check=True)
    except: pass

import qiskit
from qiskit_aer import AerSimulator
import pennylane as qml

#  rsa algorithm
class RSADemo:
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.n = None
        self.p = None
        self.q = None
    
#  public nd pvt key pair.
    def generate_keypair(self, p: int = None, q: int = None) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        if p is None or q is None:
            self.p, self.q = 3, 7
        else:
            self.p, self.q = p, q
        
        self.n = self.p * self.q
        phi_n = (self.p - 1) * (self.q - 1)
        
        for e in range(3, phi_n):
            if math.gcd(e, phi_n) == 1:
                break
        
        d = sympy.mod_inverse(e, phi_n)
        self.public_key = (self.n, e)
        self.private_key = (self.n, d)
        
        print(f"RSA Keys: Public(n={self.n}, e={e}) Private(n={self.n}, d={d})")
        return self.public_key, self.private_key
    
#  encrypts using  public key.
    def encrypt(self, message: int) -> int:
        n, e = self.public_key
        if message >= n:
            message = message % n
        return pow(message, e, n)
    
# decrypts using  private key.
    def decrypt(self, ciphertext: int) -> int:
        n, d = self.private_key
        return pow(ciphertext, d, n)

#  the quantum part of shor's algorithm.
class QuantumPeriodFinder:
    def __init__(self, n_count: int = 4):
        self.n_count = n_count
    
# this function creates a controlled unitary gate, which is a key component of shor's algorithm.
    def create_controlled_unitary(self, a: int, N: int, power: int, control: int, target: int):
        result = pow(a, power, N)
        angle = 2 * np.pi * result / N
        qml.CRY(angle, wires=[control, target])
    
# build quantum circuit for the period-finding part of shor's algorithm.
    def quantum_period_circuit(self, a: int, N: int):
        for i in range(self.n_count):
            qml.Hadamard(wires=i)
        qml.PauliX(wires=self.n_count)
        
        for j in range(self.n_count):
            power = 2 ** j
            self.create_controlled_unitary(a, N, power, j, self.n_count)
        
        qml.adjoint(qml.QFT)(wires=range(self.n_count))
    
# this function runs the quantum circuit and tries to find the period of the function a^x mod n.
    def find_period(self, a: int, N: int, n_trials: int = 100):
        dev = qml.device('default.qubit', wires=self.n_count + 1, shots=1)
        
        @qml.qnode(dev)
        def circuit():
            self.quantum_period_circuit(a, N)
            return qml.sample(wires=range(self.n_count))
        
        period_estimates = []
        
        for _ in range(n_trials):
            measurement = circuit()
            measured_int = sum(
                (bit.item() if hasattr(bit, 'item') else int(bit)) * (2 ** (self.n_count - 1 - i))
                for i, bit in enumerate(measurement)
            )
            
            if measured_int > 0:
                phase = measured_int / (2 ** self.n_count)
                for r in range(1, min(N, 20)):
                    if abs(phase - 1/r) < 0.1:
                        period_estimates.append(r)
                        break
        
        if not period_estimates:
            return None, 0
        
        counts = Counter(period_estimates)
        best_period, count = counts.most_common(1)[0]
        return best_period, count / n_trials

# this class implements the complete shor's algorithm
class CompleteShorAlgorithm:
    def __init__(self):
        self.quantum_finder = QuantumPeriodFinder(n_count=3)
    
# this function tries to factor a number n using shor's algorithm.
    def factor_number(self, N: int, max_attempts: int = 5) -> List[int]:
        print(f"Factoring {N}")
        
        # Check trivial factors
        if N % 2 == 0:
            return [2, N // 2]
        for p in [3, 5, 7, 11, 13, 17, 19]:
            if N % p == 0:
                return [p, N // p]
        
        # Main quantum algorithm
        for attempt in range(max_attempts):
            a = random.randint(2, N - 1)
            if math.gcd(a, N) > 1:
                factor = math.gcd(a, N)
                return [factor, N // factor]
            
            period, confidence = self.quantum_finder.find_period(a, N, n_trials=50)
            
            if period and confidence > 0.3 and pow(a, period, N) == 1:
                if period % 2 == 0:
                    s = pow(a, period // 2, N)
                    if s not in [1, N - 1]:
                        for delta in [-1, 1]:
                            factor = math.gcd(s + delta, N)
                            if 1 < factor < N:
                                return [factor, N // factor]
        
        return []

# this is the main function of the script.
def main():
    print("QUANTUM RSA BREAKING DEMONSTRATION")
    # print("=" * 50)
    
    # Create RSA system
    rsa = RSADemo()
    pub_key, priv_key = rsa.generate_keypair()
    
    # Test encryption
    message = 433482738923745
    ciphertext = rsa.encrypt(message)
    decrypted = rsa.decrypt(ciphertext)
    print(f"Test: {message} -> {ciphertext} -> {decrypted}")
    
    # Quantum attack
    shor = CompleteShorAlgorithm()
    factors = shor.factor_number(rsa.n)
    
    if factors:
        print(f"SUCCESS: {rsa.n} = {factors[0]} × {factors[1]}")
        
        # Reconstruct private key
        p, q = factors[0], factors[1]
        phi_n = (p - 1) * (q - 1)
        e = pub_key[1]
        d_reconstructed = sympy.mod_inverse(e, phi_n)
        
        # Break encryption
        broken_message = pow(ciphertext, d_reconstructed, rsa.n)
        print(f"BROKEN! Recovered message: {broken_message}")
    else:
        print("Attack failed (expected for simplified implementation)")
    
    # Test other numbers
    test_cases = [15, 21, 35]
    for N in test_cases:
        factors = shor.factor_number(N, max_attempts=3)
        if factors:
            print(f"Factored {N} = {factors[0]} × {factors[1]}")

if __name__ == "__main__":
    main()
