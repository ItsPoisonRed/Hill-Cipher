import nltk
from nltk.corpus import words
import numpy as np
import sys
from typing import List
from sympy import Matrix
import secrets
from typing import List

dict_inverse = {
    1: 1,
    3: 9,
    5: 21,
    7: 15,
    9: 3,
    11: 19,
    15: 7,
    17: 23,
    19: 11,
    21: 5,
    23: 17,
    25: 25,
}


def get_matrix_type(key: str) -> int:
    """Return the matrix type (2 for 2x2, 3 for 3x3) based on key length."""
    return 2 if len(key) == 4 else 3


def letter_to_number(letter: str) -> int:
    """Convert a letter to its corresponding number (0-25)."""
    return ord(letter.lower()) - ord("a")


def number_to_letter(number: int) -> str:
    """Convert a number (0-25) back to its corresponding lowercase letter."""
    return chr(number + ord("a"))


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
        return (
            matrix_key[0][0] * matrix_key[1][1] - matrix_key[0][1] * matrix_key[1][0]
        ) % 26
    elif matrix_type == 3:
        return (
            matrix_key[0][0] * matrix_key[1][1] * matrix_key[2][2]
            + matrix_key[0][1] * matrix_key[1][2] * matrix_key[2][0]
            + matrix_key[0][2] * matrix_key[1][0] * matrix_key[2][1]
            - matrix_key[0][2] * matrix_key[1][1] * matrix_key[2][0]
            - matrix_key[0][1] * matrix_key[1][0] * matrix_key[2][2]
            - matrix_key[0][0] * matrix_key[1][2] * matrix_key[2][1]
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
        nltk.data.find("corpora/words")
    except LookupError:
        nltk.download("words")
    word_list = words.words()
    filtered_words = [word for word in word_list if len(word) == 4 or len(word) == 9]
    if not filtered_words:
        print(
            "No suitable words found for key generation. Please check your NLTK installation."
        )
        sys.exit()
    while True:
        key = secrets.choice(filtered_words).lower()
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
        if det != 0 and det in dict_inverse:
            print(f"Generated key: {key}")
            return key

def is_int_pair(s):
    try:
        parts = s.split(',')
        if len(parts) != 2:
            return False
        int(parts[0].strip())
        int(parts[1].strip())
        return True
    except ValueError:
        return False