
import concurrent.futures

def gmul(a, b):
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        high_bit = a & 0x80
        a <<= 1
        if high_bit:
            a ^= 0x1b
        b >>= 1
    return result % 256

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

RCON = [
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36
]

def pad(plaintext):
    block_size = 16
    padding_length = block_size - (len(plaintext) % block_size)
    return plaintext + [padding_length] * padding_length

def unpad(padded_text):
    padding_length = padded_text[-1]
    return padded_text[:-padding_length]

def matrix_to_hex(matrix):
    return ''.join(f'{matrix[row][col]:02x}' for row in range(4) for col in range(4))

def print_state(state_matrix):
    print("State matrix:")
    for row in state_matrix:
        print(" ".join([f"{x:02x}" for x in row]))

def aes_round(state_matrix, round_key, is_final_round=False, round_num=-1):
    print(f"Round {round_num}")
    print()
    print("Before Round Transformations:")
    print_state(state_matrix)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(lambda r, c: S_BOX[state_matrix[r][c] >> 4][state_matrix[r][c] & 0x0F], r, c) for r in range(4) for c in range(4)]
        for idx, future in enumerate(futures):
            r, c = divmod(idx, 4)
            state_matrix[r][c] = future.result()
    print()
    print("After SubBytes:")
    print_state(state_matrix)

    state_matrix[1] = state_matrix[1][1:] + state_matrix[1][:1]
    state_matrix[2] = state_matrix[2][2:] + state_matrix[2][:2]
    state_matrix[3] = state_matrix[3][3:] + state_matrix[3][:3]
    print()
    print("After ShiftRows:")
    print_state(state_matrix)

    if not is_final_round:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(lambda col: [
                gmul(state_matrix[0][col], 2) ^ gmul(state_matrix[1][col], 3) ^ gmul(state_matrix[2][col], 1) ^ gmul(state_matrix[3][col], 1),
                gmul(state_matrix[0][col], 1) ^ gmul(state_matrix[1][col], 2) ^ gmul(state_matrix[2][col], 3) ^ gmul(state_matrix[3][col], 1),
                gmul(state_matrix[0][col], 1) ^ gmul(state_matrix[1][col], 1) ^ gmul(state_matrix[2][col], 2) ^ gmul(state_matrix[3][col], 3),
                gmul(state_matrix[0][col], 3) ^ gmul(state_matrix[1][col], 1) ^ gmul(state_matrix[2][col], 1) ^ gmul(state_matrix[3][col], 2)
            ], col) for col in range(4)]

            for idx, future in enumerate(futures):
                col_results = future.result()
                for row in range(4):
                    state_matrix[row][idx] = col_results[row]
        print()
        print("After MixColumns:")
        print_state(state_matrix)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(lambda r, c: state_matrix[r][c] ^ round_key[r][c], r, c) for r in range(4) for c in range(4)]
        for idx, future in enumerate(futures):
            r, c = divmod(idx, 4)
            state_matrix[r][c] = future.result()
    print()
    print("After XOR with Round Key:")
    print_state(state_matrix)

    return state_matrix

def generate_round_keys(key):
    key_schedule = [[0] * 4 for _ in range(4 * 11)]
    for i in range(4):
        for j in range(4):
            key_schedule[i][j] = key[j + i * 4]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(lambda col: key_schedule[col], col) for col in range(4, 44)]
        
        for col in range(4, 44):
            temp = [key_schedule[col - 1][row] for row in range(4)]
            if col % 4 == 0:
                temp = temp[1:] + temp[:1]
                temp = [S_BOX[b >> 4][b & 0x0F] for b in temp]
                temp[0] ^= RCON[(col // 4) - 1]
            
            for row in range(4):
                key_schedule[col][row] = key_schedule[col - 4][row] ^ temp[row]
    
    return key_schedule

def encrypt_aes(plaintext, key, num_rounds):
    if len(plaintext) % 16 != 0:
        plaintext = pad(plaintext)
    
    state_matrix = [[0] * 4 for _ in range(4)]
    for row in range(4):
        for col in range(4):
            state_matrix[row][col] = plaintext[row + col * 4]
    
    round_keys = generate_round_keys(key)
    
    state_matrix = aes_round(state_matrix, round_keys[:4], round_num=0)
    
    for round_num in range(1, num_rounds):
        state_matrix = aes_round(state_matrix, round_keys[round_num * 4:(round_num + 1) * 4], round_num=round_num)
    
    state_matrix = aes_round(state_matrix, round_keys[num_rounds * 4:], is_final_round=True, round_num=num_rounds)
    
    encrypted_text = matrix_to_hex(state_matrix)
    print("Encrypted text (hex):", encrypted_text)

def main():
    plaintext = [0x54, 0x68, 0x61, 0x74, 0x20, 0x69, 0x73, 0x20, 0x61, 0x20, 0x74, 0x65, 0x73, 0x74, 0x21, 0x21]
    key = [0x54, 0x68, 0x61, 0x74, 0x20, 0x73, 0x20, 0x6d, 0x79, 0x20, 0x4b, 0x75, 0x6e, 0x67, 0x20, 0x46]
    num_rounds = int(input("Enter the number of Encryption rounds : "))
    encrypt_aes(plaintext, key, num_rounds)

main()
