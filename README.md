
# QuantumIEEE

This repository explores RSA encryption and various methods for breaking it, from classical algorithms to a conceptual look at quantum attacks.

## Project Overview

The project is divided into three main parts:

1.  **`classic.py`**: A simple, clear demonstration of RSA encryption and decryption. It also implements two classical attacks for finding the private key:
    *   **Brute-force:** a straightforward but slow method.
    *   **Pollard's Rho:** a more efficient factoring algorithm.

2.  **`quantum.py`**: This file shows how quantum computing *could* be used to break RSA encryption. However, due to issues with quantum libraries, the code is not fully functional. It serves as a proof-of-concept and a placeholder for future development.

3.  **`low_end_lappy.py`**: An interactive, user-friendly script that allows you to:
    *   Generate your own RSA key pairs.
    *   Encrypt and decrypt messages.
    *   Simulate attacks on the encryption, including a "simulated quantum" attack (which uses classical methods for demonstration).

## How to Use

To get started, you can run the interactive script:

```bash
python low_end_lappy.py
```

This will guide you through the process of creating keys, encrypting a message, and then attempting to break the encryption.

You can also run the other scripts to see the individual components in action:


