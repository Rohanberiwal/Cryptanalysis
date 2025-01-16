# Importing necessary modules for concurrency
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


# Defining block size for AES typically uses 16-byte blocks
block_size = 16

# RCON (Round Constants) for AES key expansion, used in the key schedule
# These values are pre-defined constants used in AES to modify the round keys in key expansion
RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]
#This is a random list that I TOOK FOR THE debug output
gmul_list = []

#Comment for the SBOX (list of list)
# The S-Box (Substitution Box) used in AES encryption.
# It is a non-linear byte substitution table used to perform the substitution step in AES encryption and decryption.
# Each byte in the state matrix is substituted with a corresponding byte from the S-Box during the SubBytes step.
# The S-Box is a fixed, pre-defined 16x16 matrix, where each element is a unique byte value.
# The S-Box is designed to provide confusion, making the encryption more secure against attacks like differential and linear cryptanalysis.

SBOX = [
    [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
    [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
    [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
    [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
    [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
    [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
    [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
    [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
    [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
    [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
    [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
    [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
    [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
    [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
    [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
    [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
]

#Comment for rotate word func
# Rotates a word (list) by one position to the left, moving the first element to the last position.
def rotate(word):
    result = word[1:] + word[:1]
    return result

#Comment For sub word
# The sub_word function takes a list of bytes (word) and applies the S-box substitution
# to each byte. It processes each byte by splitting it into two nibbles: the high n (first 4 bits)
# and the low n (last 4 bits). It then uses the S-box lookup table to substitute each nibble
# with a corresponding value from the table. The transformed bytes are collected in a new list and returned.
def sub_word(word):
    transformed_word = []
    for byte in word:
        high_n = byte >> 4
        low_n = byte & 0x0F
        transformed_byte = SBOX[high_n][low_n]
        transformed_word.append(transformed_byte)
    return transformed_word


def generate_key(key):
    key_schedule = key[:]
    for i in range(16, 176, 4):
        temp = key_schedule[-4:]
        if i % 16 == 0:
            temp = sub_word(rotate(temp))
            temp[0] ^= RCON[i // 16 - 1]
        key_schedule += [key_schedule[i - 16 + j] ^ temp[j] for j in range(4)]
    return key_schedule

#Comment for printing key 
#This is the function that takes the input as matrix and then print 
#All the column it also convert the column to hexadecimal representation and then prints it sequentially 
def printer(plaintext_state_matrix):
    for col in plaintext_state_matrix:
        hex_col = [f'{value:02x}' for value in col]
        print(hex_col)
    print()


#Comment for Galois field multiplication
# This function performs Galois Field (GF) multiplication in GF(2^8), commonly used in cryptographic algorithms like AES. 
# It takes two 8-bit integers, `factor_a` and `factor_b`, and computes their product in the Galois field using bitwise operations. 
# The multiplication is carried out by iterating over each bit of `factor_b`, shifting `factor_a` left, 
# and reducing it by XORing with the irreducible polynomial `0x1b` if necessary. 
# The result is kept within 8 bits by applying modulo 256, and the final product is returned after 8 iterations.
def galois_field_multiply(factor_a, factor_b):
    num_iterations = 0
    product = 0
    while num_iterations < 8:
        if factor_b & 1:
            product ^= factor_a
        high_bit = factor_a & 0x80
        factor_a <<= 1
        if high_bit:
            factor_a ^= 0x1b  
        factor_b >>= 1
        num_iterations += 1
    gmul_list.append(product % 256)
    return product % 256


#Comment for XOR func 
# This function below performs bitwise XOR between elements of a matrix and a round key. 
# It processes a specific column (indexed by `j`) from both the `matrix` and `round_lists`, 
# where the matrix is assumed to be in a flattened form. 
# For each row, it retrieves the corresponding element from both the matrix and round key, applies the XOR operation, 
# and appends the result to `column_result`, which is then returned after processing all rows.

def xor(matrix, round_lists, j):
    column_result = []
    for i in range(4):
        matrix_value = matrix[i * 4 + j]
        round_key_value = round_lists[i * 4 + j]
        xor_result = matrix_value ^ round_key_value
        column_result.append(xor_result)
    return column_result

#comment for Round key adder function 
# The `roundkey_adder` function adds the round key to the current state matrix by performing bitwise XOR. 
# It first flattens the `state` matrix from a 4x4 structure into a 1D list, `matrix`, by iterating over each column. 
# The round key is then assigned to `round_lists`. To efficiently compute the XOR for each column, 
# the function utilizes `ThreadPoolExecutor` to parallelize the operation, calling the `xor` function for each column (indexed by `j`).
# The results of each parallelized XOR operation are gathered into the `result_matrix`, which is then returned.
def roundkey_adder(state, round_key):
    matrix = []
    for cols in range(4):
        for row in range(4):
            matrix.append(state[row][cols])
    round_lists = round_key
    result_matrix = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result_matrix = list(executor.map(lambda j: xor(matrix, round_lists, j), range(4)))
    return result_matrix

#comment for the Pad function
# The `pad` function ensures the plaintext is a multiple of the block size by adding padding bytes at the end.
# It calculates the necessary padding length and appends that many bytes, each equal to the padding length, to the plaintext.

def pad(plaintext):
    print("Since the palintext was not 16 multiple we are paddng it to nearest 16 multiple ")
    padding_length = block_size - (len(plaintext) % block_size)
    return plaintext + [padding_length] * padding_length

#Comment for the unpad function
# The `unpad` function reverses this padding process by removing the padding bytes, 
# using the last byte to determine how much padding was added.

def unpad(padded_text):
    padding_length = padded_text[-1]
    return padded_text[:-padding_length]

#Comment for subustitue row func
# The `substitute_row` function performs the SubBytes operation on a single row of the state matrix.
# It iterates through each byte in the row and looks up the corresponding byte in the 
# SBOX using the high nibble (left 4 bits) and low nibble (right 4 bits).
# The substituted byte is appended to a new list, which represents the transformed row after applying the substitution.
def substitute_row(row):
    substituted_row = []
    for b in row:
        substituted_byte = SBOX[b >> 4][b & 0x0F]
        substituted_row.append(substituted_byte)
    return substituted_row

#Comment for subustitue funcs
# The `substitution_funcs` function applies the SubBytes operation to the entire state matrix.
# It uses a `ThreadPoolExecutor` to parallelize the substitution of each row in the state matrix, improving performance.
# For each row in the state, the `substitute_row` function is called, which transforms each byte in the row using the SBOX.
# The substituted rows are collected and combined into the final substituted state matrix, which is then returned.
def substitution_funcs(state):
    substituted_state = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        substituted_state = list(executor.map(substitute_row, state))
    return substituted_state

#Comment for shift function
# The `shift_rows` function performs the ShiftRows operation on the state matrix, which is part of the AES cipher.
# It shifts the rows of the matrix cyclically to the left. 
# Row i is shifted by i positions (e.g., second row by 1, third by 2).

def shift_rows(matrix):
    for i in range(1,4):
        matrix[i] = matrix[i][i:] + matrix[i][:i]
    return matrix


#Comment for the closer func
#The cleaner function takes a 4x4 state matrix and converts each element into its corresponding
#two-digit hexadecimal representation. It iterates through the matrix, formats the values, and
#appends them to a list, which is then joined into a single string and returned. 
def cleaner(plaintext_state_matrix):
    output = []
    for r in range(4):
        for c in range(4):
            hex_value = f'{plaintext_state_matrix[c][r]:02x}'
            output.append(hex_value)
    result = ''.join(output)
    return result

#Comment for Mix col ops for colnmns
# The `mix_col_operations_for_column` function applies the MixColumns transformation
# to a single column of the state matrix. It processes the four values of the column by 
# performing Galois field multiplication with constants 0x02 and 0x03, and XORing them 
# in specific combinations as defined by the AES standard. The transformed values are then 
# placed back into the state matrix.


def mix_col_operations_for_column(column_index, plaintext_state_matrix):
    top_value = plaintext_state_matrix[0][column_index]
    upper_middle_value = plaintext_state_matrix[1][column_index]
    lower_middle_value = plaintext_state_matrix[2][column_index]
    bottom_value = plaintext_state_matrix[3][column_index]

    plaintext_state_matrix[0][column_index] = (
        galois_field_multiply(0x02, top_value) ^
        galois_field_multiply(0x03, upper_middle_value) ^
        lower_middle_value ^
        bottom_value
    )
    plaintext_state_matrix[1][column_index] = (
        top_value ^
        galois_field_multiply(0x02, upper_middle_value) ^
        galois_field_multiply(0x03, lower_middle_value) ^
        bottom_value
    )
    plaintext_state_matrix[2][column_index] = (
        top_value ^
        upper_middle_value ^
        galois_field_multiply(0x02, lower_middle_value) ^
        galois_field_multiply(0x03, bottom_value)
    )
    plaintext_state_matrix[3][column_index] = (
        galois_field_multiply(0x03, top_value) ^
        upper_middle_value ^
        lower_middle_value ^
        galois_field_multiply(0x02, bottom_value)
    )

#Comment for the Mix_col_ops
# The `mix_col_ops` function executes the MixColumns transformation for all four columns 
# in parallel. It uses a `ThreadPoolExecutor` to handle the column-wise operations concurrently, 
# improving the performance by processing each column in a separate thread. Once all columns are processed, 
# the function returns the updated state matrix.
def mix_col_ops(plaintext_state_matrix):
    with ThreadPoolExecutor() as executor:
        for column_index in range(4):
            executor.submit(mix_col_operations_for_column, column_index, plaintext_state_matrix)
    
    return plaintext_state_matrix

#Comment for the create plaintext state matrix
# The `create_plaintext_state_matrix` function takes a plaintext list and converts it into a 
# 4x4 state matrix, as required by the AES encryption algorithm. It iterates over the plaintext list, 
# collecting every 4th byte starting from the corresponding position in each column (0, 1, 2, 3) 
# to form the rows of the matrix. This transformation allows the plaintext to be represented 
# in a 4x4 grid, where each element corresponds to a byte of the input data.
# The function returns the state matrix, which is used in subsequent AES transformations.

def create_plaintext_state_matrix(plaintext_list):
    plaintext_state_matrix = []
    for i in range(4):
        row = []
        for j in range(i, len(plaintext_list), 4):
            row.append(plaintext_list[j])
        plaintext_state_matrix.append(row)
    return plaintext_state_matrix

#Comment for the AES encryption  func
# The `AES_encrypt` function performs AES encryption on the given plaintext using the provided key and number of rounds. 
# It starts by generating the key schedule and creating the initial state matrix from the plaintext. 
# The round key is added to the state matrix, and the function proceeds through multiple rounds of substitution, 
# row shifting, column mixing, and round key addition. In the final round, the column mixing step is skipped, 
# and the encrypted output is produced after the final round key is added. 
# The function prints the state matrix at each stage for debugging and visualization purposes, 
# and the final encrypted output is returned as a hexadecimal string.
def AES_encrypt(plaintext_list, key_list, rounds):

    output_key = generate_key(key_list)
    plaintext_state_matrix = create_plaintext_state_matrix(plaintext_list)
    print("State matrix ")
    printer(plaintext_state_matrix)
    key_sch =  output_key[:16]
    plaintext_state_matrix = roundkey_adder(plaintext_state_matrix, key_sch)
    print("Sate matrix after round key add")
    printer(plaintext_state_matrix)
    
    for loops in range(1, rounds):
        print("RUNNING AT STAGE ",rounds)
        plaintext_state_matrix = substitution_funcs(plaintext_state_matrix)
        print("After Substitution ")
        printer(plaintext_state_matrix)
        plaintext_state_matrix = shift_rows(plaintext_state_matrix)
        print("After shift row ops ")
        printer(plaintext_state_matrix)
        plaintext_state_matrix = mix_col_ops(plaintext_state_matrix)
        print("Afte  mix column ops ")
        printer(plaintext_state_matrix)
        plaintext_state_matrix = roundkey_adder(plaintext_state_matrix, output_key[loops*16:(loops+1)*16])
        print("After add round key ops")
        printer(plaintext_state_matrix)
        
    print("Running at the last stage")
    plaintext_state_matrix = substitution_funcs(plaintext_state_matrix)
    print("After substitution ")
    printer(plaintext_state_matrix)
    plaintext_state_matrix = shift_rows(plaintext_state_matrix)
    print("After shift row ops ")
    print()
    printer(plaintext_state_matrix)
    key_next =  output_key[rounds*16:(rounds+1)*16]
    plaintext_state_matrix = roundkey_adder(plaintext_state_matrix, key_next)
    print("addition operation")
    printer(plaintext_state_matrix)
    output = cleaner(plaintext_state_matrix)
    print()
    print("Encrypted output ", output)

#Comment for the resolve plaintext func 
# The `resolve_plaintext` function converts a hexadecimal string into a list of decimal values. 
# It processes the string by iterating over pairs of hexadecimal characters, converting each pair to a decimal value, 
# and appending it to a list. This list represents the plaintext in decimal form. 
# The function also prints the resulting list of decimal values for debugging or visualization purposes before returning it.
def resolve_plaintext(hex_string):
    plain_text = []
    for i in range(0, len(hex_string), 2):
        hex_pair = hex_string[i:i+2]
        decimal_value = int(hex_pair, 16)
        plain_text.append(decimal_value)
    
    print("This is the list for the plaintext:")
    print(plain_text)
    return plain_text

#Comment for the resolve keytype funcs
# The `resolve_ketype` function converts a hexadecimal string into a list of decimal values representing a key. 
# It processes the string by iterating over pairs of hexadecimal characters, converting each pair into its decimal equivalent, 
# and appending it to a list. This list represents the encryption/decryption key in decimal form. 
# The function prints the resulting key list for visualization or debugging before returning the list.
def resolve_ketype(hex_string):
    key_list = []
    for i in range(0, len(hex_string), 2):
        hex_pair = hex_string[i:i+2]
        decimal_value = int(hex_pair, 16)
        key_list.append(decimal_value)
    
    print("This is the list for the key:")
    print(key_list)
    return key_list

#Main func calls
# The `main` function serves as the entry point for the AES encryption process. 
# It first prompts the user to input the number of rounds for the AES encryption. 
# Then, it defines the plaintext and key in hexadecimal format, calling `resolve_ketype` to convert the key into a list of decimal values, 
# and `resolve_plaintext` to convert the plaintext hex string into a list of decimal values. 
# Finally, it invokes the `AES_encrypt` function, passing the prepared plaintext, key, and round count to perform the encryption.
def main():
    num_rounds = int(input(" enter the round "))
    if num_rounds < 0:
        print("Invalid number of the rounds")
    else :
        plaintext_hex = "3243f6a8885a308d313198a2e0370734"
        key_hex = "2b7e151628aed2a6abf7158809cf4f3c"
        key_list =  resolve_ketype(key_hex)
        plaintext_list = resolve_plaintext(plaintext_hex)
        AES_encrypt(plaintext_list , key_list, num_rounds)
    
#MAIN FUNCTION CALL     
main()
