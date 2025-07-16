import numpy as np
import random
import sys
import json
from key import load_keys, generate_key_pair
from UI import prompt_for_key, prompt_for_plaintext, prompt_for_ciphertext, print_result, parse_args
from logic import get_matrix_type, get_determinant, letter_to_number, dict_inverse, generate_key, encode, decode


def main() -> None:
    """
    Main function to run the Hill cipher tool. Handles user interaction and calls encode/decode.
    """
    print("Welcome to the Hill Cipher Tool!")
    print("Loading keys...")
    try:
        keys = load_keys()
        p = keys["p"]
        public_key = keys["public_key"]
        private_key = keys["private_key"]
        n = keys["n"]
        d = keys["d"]
    except (FileNotFoundError, json.JSONDecodeError):
        generate_key_pair()
        sys.exit()

    args = parse_args()

    # Determine mode
    if args.encode:
        mode = "encode"
    elif args.decode:
        mode = "decode"
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
            key = pow(int(args.key), int(private_key), int(p))
            key_return = public_key
        elif args.key_type == "random":
            key = generate_key()
            key_return = key
        matrix_type = get_matrix_type(key)
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
            print("Key not invertible. Please provide a different key.")
            sys.exit(1)
        text = args.text.replace(" ", "").lower()
        if mode == "encode":
            if len(text) % matrix_type != 0:
                text += "z" * (matrix_type - len(text) % matrix_type)
            message_matrix = [letter_to_number(letter) for letter in text]
            groups = [
                message_matrix[i : i + matrix_type]
                for i in range(0, len(message_matrix), matrix_type)
            ]
            result = encode(matrix_key, groups)
            print_result(result, "encode", key_return)
        else:
            ciphertext_matrix = [letter_to_number(letter) for letter in text]
            groups_cipher = [
                ciphertext_matrix[i : i + matrix_type]
                for i in range(0, len(ciphertext_matrix), matrix_type)
            ]
            result = decode(det, groups_cipher, matrix_key)
            print_result(result, "decode", key_return)
        return

    # Otherwise, fall back to interactive mode
    choice = input("Encode or Decode: ").strip().lower()
    key_return, matrix_key, matrix_type, det = prompt_for_key(p, private_key, n, d)
    if choice in ("encode", "e"):
        plaintext = prompt_for_plaintext(matrix_type)
        message_matrix = [letter_to_number(letter) for letter in plaintext]
        groups = [
            message_matrix[i : i + matrix_type]
            for i in range(0, len(message_matrix), matrix_type)
        ]
        print("Encoding...")
        result = encode(matrix_key, groups)
        print_result(result, "encode", key_return)
    elif choice in ("decode", "d"):
        ciphertext = prompt_for_ciphertext()
        ciphertext_matrix = [letter_to_number(letter) for letter in ciphertext]
        groups_cipher = [
            ciphertext_matrix[i : i + matrix_type]
            for i in range(0, len(ciphertext_matrix), matrix_type)
        ]
        print("Decoding...")
        result = decode(det, groups_cipher, matrix_key)
        print_result(result, "decode", key_return)
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
