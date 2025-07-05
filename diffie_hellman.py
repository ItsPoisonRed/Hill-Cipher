import random


def generate_private_key(n_bits, max_prime):
    random_number = random.randint(1, max_prime-1)
    return random_number

def generate_public_key(p, g, private_key):
    return g**private_key % p

def main_dh():
    n_bits = 16
    p = 5623
    g = 62061
    private_key = generate_private_key(n_bits, p)
    public_key = generate_public_key(p, g, private_key)
    print(f"p: {p}")
    print(f"g: {g}")
    print(f"public_key: {public_key}")
    return p, g, private_key, public_key