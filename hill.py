import numpy as np
from sympy import Matrix
import string
import random
import nltk
from nltk.corpus import words
import sys
import json
from typing import List, Tuple, Dict, Any
import argparse
import smtplib
from email.message import EmailMessage
import getpass

# =========================
# Hill Cipher Logic Section
# =========================

dict_inverse = {
    1:1, 3:9, 5:21, 7:15, 9:3, 11:19, 15:7, 17:23, 19:11, 21:5, 23:17, 25:25,
}

def get_matrix_type(key: str) -> int:
    """Return the matrix type (2 for 2x2, 3 for 3x3) based on key length."""
    return 2 if len(key) == 4 else 3

def letter_to_number(letter: str) -> int:
    """Convert a letter to its corresponding number (0-25)."""
    return ord(letter.lower()) - ord('a')

def number_to_letter(number: int) -> str:
    """Convert a number (0-25) back to its corresponding lowercase letter."""
    return chr(number + ord('a'))

def encode(matrix_key: np.ndarray, groups: List[List[int]]) -> str:
    """
    Encode the plaintext using the Hill cipher matrix key.
    Args:
        matrix_key: The key matrix for encoding.
        groups: List of plaintext number groups to encode.
    Returns:
        Encoded string.
    """
    encoded = ""
    for group in groups:
        group_matrix = np.array(group)
        result = np.dot(matrix_key, group_matrix) % 26
        for number in result:
            encoded += number_to_letter(number)
    return encoded

def decode(det: int, groups: List[List[int]], matrix_key: np.ndarray) -> str:
    """
    Decode the ciphertext using the Hill cipher matrix key.
    Args:
        det: Determinant of the key matrix.
        groups: List of ciphertext number groups to decode.
        matrix_key: The key matrix for decoding.
    Returns:
        Decoded string.
    """
    mult_inverse = dict_inverse[det]
    matrix_key1 = (Matrix(matrix_key).adjugate() * mult_inverse) % 26
    decoded = ""
    for group in groups:
        group_matrix = np.array(group)
        result = np.dot(matrix_key1, group_matrix) % 26
        for number in result:
            decoded += number_to_letter(number)
    return decoded

def get_determinant(matrix_key: np.ndarray, matrix_type: int) -> int:
    """
    Calculate the determinant of the key matrix modulo 26.
    Args:
        matrix_key: The key matrix.
        matrix_type: 2 for 2x2, 3 for 3x3.
    Returns:
        Determinant modulo 26.
    """
    if matrix_type == 2:
        return (matrix_key[0][0]*matrix_key[1][1] - matrix_key[0][1]*matrix_key[1][0]) % 26
    elif matrix_type == 3:
        return (
            matrix_key[0][0]*matrix_key[1][1]*matrix_key[2][2] +
            matrix_key[0][1]*matrix_key[1][2]*matrix_key[2][0] +
            matrix_key[0][2]*matrix_key[1][0]*matrix_key[2][1] -
            matrix_key[0][2]*matrix_key[1][1]*matrix_key[2][0] -
            matrix_key[0][1]*matrix_key[1][0]*matrix_key[2][2] -
            matrix_key[0][0]*matrix_key[1][2]*matrix_key[2][1]
        ) % 26
    else:
        raise ValueError("Matrix type must be 2 or 3.")

def generate_key() -> str:
    """
    Generate a random valid key (4 or 9 letter English word) for the Hill cipher.
    Returns:
        A valid key string.
    """
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words')
    word_list = words.words()
    filtered_words = [word for word in word_list if len(word) == 4 or len(word) == 9]
    if not filtered_words:
        print("No suitable words found for key generation. Please check your NLTK installation.")
        sys.exit()
    while True:
        key = random.choice(filtered_words).lower()
        matrix_type = get_matrix_type(key)
        key_matrix = [letter_to_number(letter) for letter in key]
        if matrix_type == 2:
            matrix_key = np.array([[key_matrix[0], key_matrix[1]], [key_matrix[2], key_matrix[3]]])
        else:
            matrix_key = np.array([
                [key_matrix[0], key_matrix[1], key_matrix[2]],
                [key_matrix[3], key_matrix[4], key_matrix[5]],
                [key_matrix[6], key_matrix[7], key_matrix[8]]
            ])
        det = get_determinant(matrix_key, matrix_type)
        if det != 0 and det in dict_inverse:
            print(f"Generated key: {key}")
            return key

# =========================
# Key Management Section
# =========================

def generate_key_pair() -> None:
    """
    Generate a Diffie-Hellman key pair and save it to a JSON file.
    """
    from diffie_hellman import main_dh
    p, g, private_key, public_key = main_dh()
    with open("key_pair.json", "w") as file:
        json.dump({"p": p, "g": g, "private_key": private_key, "public_key": public_key}, file)

def load_keys(filename: str = "key_pair.json") -> Dict[str, Any]:
    """
    Load Diffie-Hellman keys from a JSON file.
    Args:
        filename: Path to the key file.
    Returns:
        Dictionary with keys 'p', 'g', 'private_key', 'public_key'.
    """
    with open(filename, "r") as file:
        return json.load(file)

# =========================
# User Interface Section
# =========================

def prompt_for_key(p: int, private_key: int) -> Tuple[str, np.ndarray, int, int]:
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
        key_input = input(
            "Enter the key (4 or 9 letters), a seed (integer), a public key (integer), or 'random':\n"
            "  - Example key: 'test' or 'algorithm'\n"
            "  - Example seed: 12345\n"
            "  - Example public key: 67890\n"
            "  - Or type 'random' for a random key\n> "
        ).strip().lower().translate(str.maketrans("", "", string.punctuation)).replace(" ", "")
        if key_input.isdigit():
            print(f"Using seed/public key: {key_input}")
            num_type = input("Is this a public key or a seed? (p/s): ").strip().lower()
            if num_type == "p":               
                key_p = int(key_input) ** int(private_key) % int(p)
                random.seed(key_p)
                key = generate_key()
                key_return = key_input
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
                matrix_key = np.array([[key_matrix[0], key_matrix[1]], [key_matrix[2], key_matrix[3]]])
            else:
                matrix_key = np.array([
                    [key_matrix[0], key_matrix[1], key_matrix[2]],
                    [key_matrix[3], key_matrix[4], key_matrix[5]],
                    [key_matrix[6], key_matrix[7], key_matrix[8]]
                ])
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
    plaintext = input("Enter plaintext: ").replace(" ", "").strip().lower().translate(str.maketrans("", "", string.punctuation))
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
    ciphertext = input("Enter ciphertext: ").replace(" ", "").strip().lower().translate(str.maketrans("", "", string.punctuation))
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
    if mode == 'encode':
        print(f"Encoded text: {result}\n")
        send_email(key, result)
        
    else:
        print(f"Decoded text: {result}\n")
        send_email(key, result)

def parse_args():
    """
    Parse command-line arguments for mode, key, and text.
    Returns:
        Namespace with attributes: encode, decode, key, text
    """
    parser = argparse.ArgumentParser(description="Hill Cipher Command-Line Tool")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--encode', action='store_true', help='Encode mode')
    group.add_argument('-d', '--decode', action='store_true', help='Decode mode')
    parser.add_argument('--key-type', type=str, help='Key type (key, seed, public key, random)')
    parser.add_argument('--key', type=str, help='Key to use (4 or 9 letters)')
    parser.add_argument('--text', type=str, help='Text to encode or decode')
    return parser.parse_args()

# =========================
# Email Section
# =========================

def send_email(key: str, result: str) -> None:
    """
    Send the encoded text to the user's email.
    Args:
        file: Path to the file containing the encoded text.
    """
    email = input("Would you like to send the encoded text to your email? (y/n): ").strip().lower()
    if email == "y":
        user_email = input("Enter your email: ").strip()
        sender_email = input("Enter the recipient's email: ").strip()
        msg = EmailMessage()
        msg.set_content(result)
        msg["Subject"] = "Encoded Text"
        msg["From"] = user_email
        msg["To"] = sender_email
        password = getpass.getpass("Enter your app password: ")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(user_email, password)
            server.send_message(msg)
            print("Email sent successfully!")
    else:
        print("Email not sent.")

# =========================
# Main Application Section
# =========================

def main() -> None:
    """
    Main function to run the Hill cipher tool. Handles user interaction and calls encode/decode.
    """
    print("Welcome to the Hill Cipher Tool!")
    try:
        keys = load_keys()
        p = keys["p"]
        private_key = keys["private_key"]
    except (FileNotFoundError, json.JSONDecodeError):
        generate_key_pair()
        sys.exit()

    args = parse_args()

    # Determine mode
    if args.encode:
        mode = 'encode'
    elif args.decode:
        mode = 'decode'
    else:
        mode = None

    # If all CLI args are provided, run in CLI mode
    if mode and args.text and args.key_type:
        if args.key_type == "key":
            key = args.key.lower()
            if not key.isalpha() or len(key) not in (4, 9):
                print("Key must be 4 or 9 letters.")
                sys.exit(1)
            key_return = key
        elif args.key_type == "seed":
            random.seed(int(args.key))
            key = generate_key()
            key_return = args.key
        elif args.key_type == "public key":
            key = int(args.key) ** int(private_key) % int(p)
            key_return = args.key
        elif args.key_type == "random":
            key = generate_key()
            key_return = key
        matrix_type = get_matrix_type(key)
        key_matrix = [letter_to_number(letter) for letter in key]
        if matrix_type == 2:
            matrix_key = np.array([[key_matrix[0], key_matrix[1]], [key_matrix[2], key_matrix[3]]])
        else:
            matrix_key = np.array([
                [key_matrix[0], key_matrix[1], key_matrix[2]],
                [key_matrix[3], key_matrix[4], key_matrix[5]],
                [key_matrix[6], key_matrix[7], key_matrix[8]]
            ])
        det = get_determinant(matrix_key, matrix_type)
        if det == 0 or det not in dict_inverse:
            print("Key not invertible. Please provide a different key.")
            sys.exit(1)
        text = args.text.replace(" ", "").lower()
        if mode == 'encode':
            if len(text) % matrix_type != 0:
                text += "z" * (matrix_type - len(text) % matrix_type)
            message_matrix = [letter_to_number(letter) for letter in text]
            groups = [message_matrix[i:i+matrix_type] for i in range(0, len(message_matrix), matrix_type)]
            result = encode(matrix_key, groups)
            print_result(result, 'encode', key_return)
        else:
            ciphertext_matrix = [letter_to_number(letter) for letter in text]
            groups_cipher = [ciphertext_matrix[i:i+matrix_type] for i in range(0, len(ciphertext_matrix), matrix_type)]
            result = decode(det, groups_cipher, matrix_key)
            print_result(result, 'decode', key_return)
        return

    # Otherwise, fall back to interactive mode
    key_return, matrix_key, matrix_type, det = prompt_for_key(p, private_key)
    choice = input("Encode or Decode: ").strip().lower()
    if choice in ("encode", "e"):
        plaintext = prompt_for_plaintext(matrix_type)
        message_matrix = [letter_to_number(letter) for letter in plaintext]
        groups = [message_matrix[i:i+matrix_type] for i in range(0, len(message_matrix), matrix_type)]
        print("Encoding...")
        result = encode(matrix_key, groups)
        print_result(result, 'encode', key_return)
    elif choice in ("decode", "d"):
        ciphertext = prompt_for_ciphertext()
        ciphertext_matrix = [letter_to_number(letter) for letter in ciphertext]
        groups_cipher = [ciphertext_matrix[i:i+matrix_type] for i in range(0, len(ciphertext_matrix), matrix_type)]
        print("Decoding...")
        result = decode(det, groups_cipher, matrix_key)
        print_result(result, 'decode', key_return)
    else:
        print("Invalid choice. Please enter 'encode' or 'decode'.")
    print("Thank you for using the Hill Cipher Tool!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)