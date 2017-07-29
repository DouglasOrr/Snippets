# Factor a badly generated modulus

import sys
import gmpy2
from gmpy2 import mpz

def factor_simple(N):
    A = gmpy2.isqrt(N) + 1
    x = gmpy2.isqrt(A*A - N)
    return (A - x, A + x)

def factor_scan(N):
    A = gmpy2.isqrt(N) + 1
    while True:
        x = gmpy2.isqrt(A*A - N)
        if gmpy2.f_mod(N, A-x) == 0:
            return (A - x, A + x)
        A += 1

def ordered_factors(p, q):
    return (p, q) if p < q else (q, p)

def factor_scan_32(N):
    dA = gmpy2.isqrt(4 * 6 * N) + 1
    while True:
        x = gmpy2.isqrt(dA*dA - 24*N)
        p1 = (dA + x) / 6
        if gmpy2.f_mod(N, p1) == 0:
            return ordered_factors(p1, N/p1)
        p2 = (dA - x) / 6
        if gmpy2.f_mod(N, p2) == 0:
            return ordered_factors(p2, N/p2)
        dA += 1

# input
N=mpz(sys.argv[2])
print("# N=%d" % N)

# factor
mode=sys.argv[1]
if mode == "average":
    (p,q) = factor_simple(N)
elif mode == "scan":
    (p,q) = factor_scan(N)
elif mode == "scan_32":
    (p,q) = factor_scan_32(N)
else:
    error("Unknown mode " + mode)

# output
print("# Check match? %r  p.prime? %r  q.prime? %r" % (N == p*q, gmpy2.is_prime(p), gmpy2.is_prime(q)))
print(p)
