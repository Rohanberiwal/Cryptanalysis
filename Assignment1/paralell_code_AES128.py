import concurrent.futures


S_BOX = [
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


ROUND_CONSTANTS = [
    [0x00, 0x00, 0x00, 0x00],
    [0x01, 0x00, 0x00, 0x00],
    [0x02, 0x00, 0x00, 0x00],
    [0x04, 0x00, 0x00, 0x00],
    [0x08, 0x00, 0x00, 0x00],
    [0x10, 0x00, 0x00, 0x00],
    [0x20, 0x00, 0x00, 0x00],
    [0x40, 0x00, 0x00, 0x00],
    [0x80, 0x00, 0x00, 0x00],
    [0x1b, 0x00, 0x00, 0x00],
    [0x36, 0x00, 0x00, 0x00]
]

# Helper function to perform Galois Field multiplication (GF(2^8))
def gmul(a, b):
    result = 0
    for loop in range(8):
        if b & 1:
            result ^= a
        high_bit = a & 0x80
        a <<= 1
        if high_bit:
            a ^= 0x1b
        b >>= 1
    return result % 256

# Perform a SubBytes operation in parallel
def apply_sub_bytes(matrix):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for row in range(4):
            for col in range(4):
                futures.append(executor.submit(substitute_byte, matrix, row, col))
        # Wait for all futures to complete
        concurrent.futures.wait(futures)
    return matrix

def substitute_byte(matrix, row, col):
    matrix[row][col] = S_BOX[matrix[row][col] >> 4][matrix[row][col] & 0x0F]

# Shift the rows of the state matrix in parallel
def apply_shift_rows(matrix):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        futures.append(executor.submit(shift_row, matrix, 1, 1))
        futures.append(executor.submit(shift_row, matrix, 2, 2))
        futures.append(executor.submit(shift_row, matrix, 3, 3))
        # Wait for all futures to complete
        concurrent.futures.wait(futures)
    return matrix

def shift_row(matrix, row_index, shift_amount):
    matrix[row_index] = matrix[row_index][shift_amount:] + matrix[row_index][:shift_amount]

# Mix the columns of the state matrix in parallel
def apply_mix_columns(matrix):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for col in range(4):
            futures.append(executor.submit(mix_column, matrix, col))
        # Wait for all futures to complete
        concurrent.futures.wait(futures)
    return matrix

def mix_column(matrix, col):
    temp = [matrix[0][col], matrix[1][col], matrix[2][col], matrix[3][col]]
    matrix[0][col] = gmul(temp[0], 2) ^ gmul(temp[1], 3) ^ gmul(temp[2], 1) ^ gmul(temp[3], 1)
    matrix[1][col] = gmul(temp[0], 1) ^ gmul(temp[1], 2) ^ gmul(temp[2], 3) ^ gmul(temp[3], 1)
    matrix[2][col] = gmul(temp[0], 1) ^ gmul(temp[1], 1) ^ gmul(temp[2], 2) ^ gmul(temp[3], 3)
    matrix[3][col] = gmul(temp[0], 3) ^ gmul(temp[1], 1) ^ gmul(temp[2], 1) ^ gmul(temp[3], 2)

# XOR the state with the round key
def xor_with_round_key(matrix, round_key):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for row in range(4):
            for col in range(4):
                futures.append(executor.submit(xor_byte, matrix, row, col, round_key))
        # Wait for all futures to complete
        concurrent.futures.wait(futures)
    return matrix

def xor_byte(matrix, row, col, round_key):
    matrix[row][col] ^= round_key[row][col]

# Expand the key for multiple rounds
def generate_round_keys(key):
    key_schedule = [[0] * 4 for _ in range(4 * 11)]
    key_bytes = [ord(char) for char in key]
    
    for i in range(4):
        for j in range(4):
            key_schedule[i][j] = key_bytes[j + i * 4]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for col in range(4, 44):
            futures.append(executor.submit(expand_key_column, key_schedule, col))
        concurrent.futures.wait(futures)
    
    return key_schedule

def expand_key_column(key_schedule, col):
    temp = [key_schedule[col - 1][row] for row in range(4)]
    if col % 4 == 0:
        temp = temp[1:] + temp[:1]
        temp = [S_BOX[b >> 4][b & 0x0F] for b in temp]
        temp[0] ^= ROUND_CONSTANTS[col // 4][0]
    
    for row in range(4):
        key_schedule[col][row] = key_schedule[col - 4][row] ^ temp[row]

# Convert the state matrix to a string
def matrix_to_string(matrix):
    return ''.join(chr(matrix[row][col]) for row in range(4) for col in range(4))

# AES Encryption Function
def encrypt_aes(plaintext, key):
    state_matrix = [[0] * 4 for _ in range(4)]
    
    for row in range(4):
        for col in range(4):
            state_matrix[row][col] = ord(plaintext[row + col * 4])
    
    round_keys = generate_round_keys(key)
    state_matrix = xor_with_round_key(state_matrix, round_keys[:4])
    
    for round_num in range(1, 10):
        state_matrix = apply_sub_bytes(state_matrix)
        state_matrix = apply_shift_rows(state_matrix)
        state_matrix = apply_mix_columns(state_matrix)
        state_matrix = xor_with_round_key(state_matrix, round_keys[round_num * 4:(round_num + 1) * 4])
    
    state_matrix = apply_sub_bytes(state_matrix)
    state_matrix = apply_shift_rows(state_matrix)
    state_matrix = xor_with_round_key(state_matrix, round_keys[40:])
    
    return matrix_to_string(state_matrix)

# Main function to initiate AES encryption
def main():
    plaintext = "This is a test!!"
    key = "Thats my Kung Fu"
    encrypted_text = encrypt_aes(plaintext, key)
    print("Ouptut of AES 128 :", encrypted_text)

main()
