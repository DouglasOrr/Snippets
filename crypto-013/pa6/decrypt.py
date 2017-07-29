# Decrypt RSA given a factorization

import sys
import gmpy2
from gmpy2 import mpz

ciphertext = mpz(sys.argv[1])
n = mpz(sys.argv[2])
e = mpz(sys.argv[3])
p = mpz(sys.argv[4])

q = n / p
totient = (p-1) * (q-1)
d = gmpy2.powmod(e, -1, totient)
plain = gmpy2.powmod(ciphertext, d, n)

# grab the ascii bytes
mask = mpz(1)
text = ""
while mask < plain:
    char = chr((plain / mask) % 256)
    if char == '\0':
        break
    else:
        text = char + text
        mask *= 256

print(text)
