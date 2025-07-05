import numpy as np
from sympy import Matrix
import string
import random
import nltk
from nltk.corpus import words
from diffie_hellman import *
import sys

dict_inverse = {
    1:1, 3:9, 5:21, 7:15, 9:3, 11:19, 15:7, 17:23, 19:11, 21:5, 23:17, 25:25,
}

def get_matrix_type(key: str) -> int:
    return 2 if len(key) == 4 else 3

def letter_to_number(letter: str) -> int:
    return ord(letter.lower()) - ord('a')

def number_to_letter(number: int) -> str:
    return chr(number + ord('a'))

def encode(matrix_key: np.ndarray, groups: list[list[int]]) -> None:
    for group in groups:
        group_matrix = np.array(group)
        result = np.dot(matrix_key, group_matrix) % 26
        for number in result:
            print(number_to_letter(number), end="")
    print()

def decode(det: int, groups: list[list[int]], matrix_key: np.ndarray) -> None:
    mult_inverse = dict_inverse[det]
    matrix_key1 = (Matrix(matrix_key).adjugate() * mult_inverse) % 26
    for group in groups:
        group_matrix = np.array(group)
        result = np.dot(matrix_key1, group_matrix) % 26
        for number in result:
            print(number_to_letter(number), end="")
    print()

def get_determinant(matrix_key: np.ndarray, matrix_type: int) -> int:
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
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words')
    word_list = words.words()
    filtered_words = [word for word in word_list if len(word) == 4 or len(word) == 9]
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

def get_matrix() -> tuple[np.ndarray, int, int]:
    global p, private_key
    while True:
        key_input = input("Enter the key (4 or 9 letters), a seed (integer), a public key (integer), or 'random': ").strip().lower().translate(str.maketrans("", "", string.punctuation)).replace(" ", "")
        if key_input.isdigit():
            num_type = input("Is this a public key or a seed? (p/s): ").strip().lower()
            if num_type == "p":               
                key_p = int(key_input) ** int(private_key) % int(p)
                random.seed(key_p)
                key = generate_key()
            else:
                random.seed(int(key_input))
                key = generate_key()
            matrix_type = get_matrix_type(key)
        elif key_input == "random" or key_input == "r":
            key = generate_key()
            matrix_type = get_matrix_type(key)
        else:
            key = key_input
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
                print("Key not invertible, generating a new one...")
                key = generate_key()
                continue
            return matrix_key, matrix_type, det

def generate_key_pair():
    p, g, private_key, public_key = main_dh()
    with open("key_pair.txt", "w") as file:
        file.write(f"p: {p}\ng: {g}\nprivate_key: {private_key}\npublic_key: {public_key}")

def main():
    matrix_key, matrix_type, det = get_matrix()
    choice = input("Encode or Decode: ").strip().lower()
    if choice == "encode" or choice == "e":
        plaintext = input("Enter plaintext: ").replace(" ", "").strip().lower().translate(str.maketrans("", "", string.punctuation))
        if len(plaintext) % matrix_type != 0:
            plaintext += "z" * (matrix_type - len(plaintext) % matrix_type)
        message_matrix = [letter_to_number(letter) for letter in plaintext]
        groups = [message_matrix[i:i+matrix_type] for i in range(0, len(message_matrix), matrix_type)]
        encode(matrix_key, groups)
    elif choice == "decode" or choice == "d":
        ciphertext = input("Enter ciphertext: ").replace(" ", "").strip().lower().translate(str.maketrans("", "", string.punctuation))
        ciphertext_matrix = [letter_to_number(letter) for letter in ciphertext]
        groups_cipher = [ciphertext_matrix[i:i+matrix_type] for i in range(0, len(ciphertext_matrix), matrix_type)]
        decode(det, groups_cipher, matrix_key)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    try:
        with open("key_pair.txt", "r") as file:
            lines = file.read().splitlines()
            p = int(lines[0][3:])  # remove 'p: '
            g = int(lines[1][3:])  # remove 'g: '
            private_key = int(lines[2][12:])  # remove 'private_key: '
            public_key = int(lines[3][11:])  # remove 'public_key: '
    except FileNotFoundError:
        generate_key_pair()
        sys.exit()
    main()