import random
import numpy as np
from sympy import nextprime

def get_n_bits(n_bits=16):
    input_n_bits = input(f"Enter the number of bits for the prime number (default: {n_bits}): ")
    if input_n_bits == "":
        return n_bits
    else:
        return int(input_n_bits)

def random_prime_up_to_n_bits(n_bits):
    rand_num = random.getrandbits(n_bits)
    rand_num = max(2, rand_num)
    return nextprime(rand_num)

def generate_random_number_up_to_n_bits(n_bits):
    return random.getrandbits(n_bits)

def generate_private_key(n_bits, max_prime):
    random_number = random.randint(1, max_prime-1)
    return random_number

def generate_public_key(p, g, private_key):
    return g**private_key % p

def main_dh():
    n_bits = get_n_bits()
    p = random_prime_up_to_n_bits(n_bits)
    g = generate_random_number_up_to_n_bits(n_bits)
    private_key = generate_private_key(n_bits, p)
    public_key = generate_public_key(p, g, private_key)
    print(f"p: {p}")
    print(f"g: {g}")
    print(f"public_key: {public_key}")
    return p, g, private_key, public_key