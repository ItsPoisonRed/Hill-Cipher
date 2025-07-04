import numpy as np
from sympy import Matrix
import string
import random
import nltk
from nltk.corpus import words

nltk.download('words')

def letter_to_number(letter):
    return ord(letter.lower()) - ord('a')

def number_to_letter(number):
    return chr(number + ord('a'))

def encode(matrix_key, groups):
    for group in groups:
        group_matrix = np.array(group)
        result = np.dot(matrix_key, group_matrix) % 26
        for number in result:
            letter = number_to_letter(number)
            print(letter, end="")

dict_inverse = {
    1:1,
    3:9,
    5:21,
    7:15,
    9:3,
    11:19,
    15:7,
    17:23,
    19:11,
    21:5,
    23:17,
    25:25,
}

def decode_2x2(det, groups, matrix_key):
    for group in groups:
        group_matrix = np.array(group)
        mult_inverse = dict_inverse[det]
        matrix_key1 = (Matrix(matrix_key).adjugate()*mult_inverse)%26
        result = np.dot(matrix_key1, group_matrix) % 26
        for number in result:
            letter = number_to_letter(number)
            print(letter, end="")
        
def decode_3x3(det, groups, matrix_key):
    for group in groups:
        group_matrix = np.array(group)
        mult_inverse = dict_inverse[det]
        matrix_key1 = (Matrix(matrix_key).adjugate()*mult_inverse)%26
        result = np.dot(matrix_key1, group_matrix) % 26
        for number in result:
            letter = number_to_letter(number)
            print(letter, end="")

def generate_key():
    word_list = words.words()
    filtered_words = [word for word in word_list if len(word) == 4 or len(word) == 9]
    while True:
        key = random.choice(filtered_words)
        if len(key) == 4:
            print(f"Generated key: {key}")
            return key
        elif len(key) == 9:
            print(f"Generated key: {key}")
            return key
        else:
            continue


key= input("Enter the key or enter seed: ").strip().lower().translate(str.maketrans("", "", string.punctuation)).replace(" ", "")
if key.isdigit():
    random.seed(int(key))
    key = generate_key()
else:
    pass

while True:
    key_matrix = [letter_to_number(letter) for letter in key]
    if len(key_matrix) == 4:
        matrix_type = 2
        matrix_key = np.array([[key_matrix[0], key_matrix[1]], [key_matrix[2], key_matrix[3]]])
        det = (matrix_key[0][0]*matrix_key[1][1] - matrix_key[0][1]*matrix_key[1][0]) % 26
        if det == 0 or det % 2 == 0 or det % 13 == 0:
            print("Key not invertible, generating a new one...")
            key = generate_key()
            continue
        break
    elif len(key_matrix) == 9:
        matrix_type = 3
        matrix_key = np.array([[key_matrix[0], key_matrix[1], key_matrix[2]], [key_matrix[3], key_matrix[4], key_matrix[5]], [key_matrix[6], key_matrix[7], key_matrix[8]]])
        det = (matrix_key[0][0]*matrix_key[1][1]*matrix_key[2][2] +
               matrix_key[0][1]*matrix_key[1][2]*matrix_key[2][0] +
               matrix_key[0][2]*matrix_key[1][0]*matrix_key[2][1] -
               matrix_key[0][2]*matrix_key[1][1]*matrix_key[2][0] -
               matrix_key[0][1]*matrix_key[1][0]*matrix_key[2][2] -
               matrix_key[0][0]*matrix_key[1][2]*matrix_key[2][1]) % 26
        if det == 0 or det % 2 == 0 or det % 13 == 0:
            print("Key not invertible, generating a new one...")
            key = generate_key()
            continue
        break
    else:
        raise ValueError("Key matrix must be 2x2 or 3x3")

choice = input("Choose an option (Encode or Decode): ").replace(" ", "").strip().upper()

if choice == "ENCODE":
    Plaintext = input("Enter the plaintext: ").replace(" ", "").strip().lower().translate(str.maketrans("", "", string.punctuation))
    Message_matrix = []
    if len(Plaintext)%matrix_type!=0:
        Plaintext += "z"*(matrix_type-len(Plaintext)%matrix_type)
    for letter in Plaintext:
        letter_number = letter_to_number(letter)
        Message_matrix.append(letter_number)

    groups = []
    for i in range(0, len(Message_matrix), matrix_type):
        groups.append(Message_matrix[i:i+matrix_type])

    encode(matrix_key, groups)

elif choice == "DECODE":
    Ciphertext = input("Enter the ciphertext: ").replace(" ", "").strip().lower().translate(str.maketrans("", "", string.punctuation))
    Ciphertext_matrix = []
    for letter in Ciphertext:
        letter_number = letter_to_number(letter)
        Ciphertext_matrix.append(letter_number)

    groups_cipher = []
    for i in range(0, len(Ciphertext_matrix), matrix_type):
        groups_cipher.append(Ciphertext_matrix[i:i+matrix_type])

    if matrix_type == 2:
        decode_2x2(det, groups_cipher, matrix_key)
    else:
        decode_3x3(det, groups_cipher, matrix_key)

else:
    raise ValueError("Invalid choice")

    
    

