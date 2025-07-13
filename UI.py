import numpy as np
import string
import random
import secrets
from typing import Tuple
from logic import get_matrix_type, get_determinant, letter_to_number, dict_inverse, generate_key, is_int_pair
import sys
import argparse
from email_utils import send_email
from key import load_keys


def prompt_for_key(p: int, private_key: int, n: int, d: int) -> Tuple[str, np.ndarray, int, int]:
    """
    Prompt the user for a key, seed, public key, or random, and return a valid Hill cipher matrix.
    Args:
        p: Diffie-Hellman prime modulus.
        private_key: Diffie-Hellman private key.
    Returns:
        matrix_key: The valid key matrix.
        matrix_type: 2 or 3.
        det: Determinant of the matrix.
    """
    while True:
        key_input = (
            input(
                "Enter the key (4 or 9 letters), a seed (integer), a public key (integer), or 'random':\n"
                "  - Example key: 'test' or 'algorithm'\n"
                "  - Example seed: 12345\n"
                "  - Example Diffie-Hellman public key: 67890 or RSA public key: 67890, 12345\n"
                "  - Or type 'random' for a random key\n> "
            )
            .strip()
            .lower()
            .translate(str.maketrans("", "", string.punctuation))
            .replace(" ", "")
        )
        if key_input.isdigit():
            print(f"Using seed/public key: {key_input}")
            num_type = input("Is this a public key or a seed? (p/s): ").strip().lower()
            if num_type == "p":
                key_protocol = input("Would you like to use RSA Trapdoor Permutation or Diffie-Hellman Protocol? (r/d): ").strip().lower()
                if key_protocol == "r":
                    key_p = int(key_input) ** int(d) % int(n)
                    random.seed(key_p)
                    key = generate_key()
                    keys = load_keys()
                    key_return = keys["e"],keys["n"]
                else:
                    key_p = int(key_input) ** int(private_key) % int(p)
                    random.seed(key_p)
                    key = generate_key()
                    keys = load_keys()
                    key_return = keys["public_key"]
            else:
                random.seed(int(key_input))
                key = generate_key()
                key_return = key_input
            matrix_type = get_matrix_type(key)
        elif key_input in ("random", "r"):
            print("Generating a random key...")
            key = generate_key()
            matrix_type = get_matrix_type(key)
            key_return = key
        elif is_int_pair(key_input):
                key_num=secrets.randbits(1024)
                parts=key_input.split(',')
                key_num2=key_num*int(parts[0])%int(parts[1])
                random.seed(key_num2)
                key=generate_key()
                key_return=key
        else:
            key = key_input
            if not key.isalpha():
                print("Key must only contain letters.")
                continue
            key_return = key
            if len(key) == 4:
                matrix_type = 2
            elif len(key) == 9:
                matrix_type = 3
            else:
                print("Key must be 4 or 9 letters.")
                continue
        while True:
            key_matrix = [letter_to_number(letter) for letter in key]
            if matrix_type == 2:
                matrix_key = np.array(
                    [[key_matrix[0], key_matrix[1]], [key_matrix[2], key_matrix[3]]]
                )
            else:
                matrix_key = np.array(
                    [
                        [key_matrix[0], key_matrix[1], key_matrix[2]],
                        [key_matrix[3], key_matrix[4], key_matrix[5]],
                        [key_matrix[6], key_matrix[7], key_matrix[8]],
                    ]
                )
            det = get_determinant(matrix_key, matrix_type)
            if det == 0 or det not in dict_inverse:
                print("Key not invertible, generating a new one... Please wait.")
                key = generate_key()
                continue
            print("Key is valid and invertible.")
            return key_return, matrix_key, matrix_type, det

def prompt_for_plaintext(matrix_type: int) -> str:
    """
    Prompt the user for plaintext and validate it.
    Args:
        matrix_type: 2 or 3 (for padding).
    Returns:
        Validated and padded plaintext string.
    """
    plaintext = (
        input("Enter plaintext: ")
        .replace(" ", "")
        .strip()
        .lower()
        .translate(str.maketrans("", "", string.punctuation))
    )
    if not plaintext:
        print("Plaintext cannot be empty.")
        sys.exit()
    if not plaintext.isalpha():
        print("Warning: Non-letter characters will be removed from plaintext.")
    if len(plaintext) % matrix_type != 0:
        print(f"Plaintext length not a multiple of {matrix_type}, padding with 'z'.")
        plaintext += "z" * (matrix_type - len(plaintext) % matrix_type)
    return plaintext


def prompt_for_ciphertext() -> str:
    """
    Prompt the user for ciphertext and validate it.
    Returns:
        Validated ciphertext string.
    """
    ciphertext = (
        input("Enter ciphertext: ")
        .replace(" ", "")
        .strip()
        .lower()
        .translate(str.maketrans("", "", string.punctuation))
    )
    if not ciphertext:
        print("Ciphertext cannot be empty.")
        sys.exit()
    if not ciphertext.isalpha():
        print("Warning: Non-letter characters will be removed from ciphertext.")
    return ciphertext


def print_result(result: str, mode: str, key: str) -> None:
    """
    Print the encoded or decoded result.
    Args:
        result: The resulting string.
        mode: 'encode' or 'decode'.
    """
    if mode == "encode":
        return_string = (f"Encoded text: {result}\nKey: {key}")
        print(return_string)
        send_email(return_string, mode)

    else:
        return_string = (f"Key: {key}")
        print(return_string)
        send_email(return_string, mode)


def parse_args():
    """
    Parse command-line arguments for mode, key, and text.
    Returns:
        Namespace with attributes: encode, decode, key, text
    """
    parser = argparse.ArgumentParser(description="Hill Cipher Command-Line Tool")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--encode", action="store_true", help="Encode mode")
    group.add_argument("-d", "--decode", action="store_true", help="Decode mode")
    parser.add_argument(
        "--key-type", type=str, help="Key type (key, seed, public key, random)"
    )
    parser.add_argument("--key", type=str, help="Key to use (4 or 9 letters)")
    parser.add_argument("--text", type=str, help="Text to encode or decode")
    return parser.parse_args()