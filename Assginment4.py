block_size = 16
RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]
gmul_list = []
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

def rotate(word):
    result = word[1:] + word[:1]
    return result

def sub_word(word):
    transformed_word = []
    for byte in word:
        high_nibble = byte >> 4
        low_nibble = byte & 0x0F
        transformed_byte = SBOX[high_nibble][low_nibble]
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

def printer(plaintext_state_matrix):
    for col in plaintext_state_matrix:
        hex_col = [f'{value:02x}' for value in col]
        print(hex_col)
    print()

def galois_field_multiply(factor_a, factor_b):
    product = 0
    num_iterations = 0
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

def roundkey_adder(state, round_key):
    matrix = []
    for cols in range(4):
        for row in range(4):
            matrix.append(state[row][cols])
    
    round_lists = round_key
    result_matrix = []

    for j in range(4):
        column_result = []
        for i in range(4):
            matrix_value = matrix[i * 4 + j]
            round_key_value = round_lists[i * 4 + j]
            xor_result = matrix_value ^ round_key_value
            column_result.append(xor_result)
        result_matrix.append(column_result)

    return result_matrix

def pad(plaintext):
    print("Since the palintext was not 16 multiple we are paddng it to nearest 16 multiple ")
    padding_length = block_size - (len(plaintext) % block_size)
    return plaintext + [padding_length] * padding_length



def unpad(padded_text):
    padding_length = padded_text[-1]
    return padded_text[:-padding_length]


def subustution_funcs(state):
    substituted_state = []
    for row in state:
        substituted_row = []
        for b in row:
            substituted_byte = SBOX[b >> 4][b & 0x0F]
            substituted_row.append(substituted_byte)
        substituted_state.append(substituted_row)
    return substituted_state

def shift_rows(state_matrix):
    for i in range(1,4):
        state_matrix[i] = state_matrix[i][i:] + state_matrix[i][:i]
    return state_matrix

def cleaner(plaintext_state_matrix):
    output = []
    for r in range(4):
        for c in range(4):
            hex_value = f'{plaintext_state_matrix[c][r]:02x}'
            output.append(hex_value)
    result = ''.join(output)
    return result


def mix_col_ops(plaintext_state_matrix):
    column_index = 0
    while column_index < 4:
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
        column_index += 1
    
    return plaintext_state_matrix

def create_plaintext_state_matrix(plaintext_list):
    plaintext_state_matrix = []
    for i in range(4):
        row = []
        for j in range(i, len(plaintext_list), 4):
            row.append(plaintext_list[j])
        plaintext_state_matrix.append(row)
    return plaintext_state_matrix

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
        plaintext_state_matrix = subustution_funcs(plaintext_state_matrix)
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
    plaintext_state_matrix = subustution_funcs(plaintext_state_matrix)
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
    return output

def resolve_plaintext(hex_string):
    plain_text = []
    for i in range(0, len(hex_string), 2):
        hex_pair = hex_string[i:i+2]
        decimal_value = int(hex_pair, 16)
        plain_text.append(decimal_value)
    
    print("This is the list for the plaintext:")
    print(plain_text)
    return plain_text

def resolve_ketype(hex_string):
    key_list = []
    for i in range(0, len(hex_string), 2):
        hex_pair = hex_string[i:i+2]
        decimal_value = int(hex_pair, 16)
        key_list.append(decimal_value)
    
    print("This is the list for the key:")
    print(key_list)
    return key_list

def distinguishingAttack(oracle, key, numRounds):
    constant = []
    for i in range(15):
        constant.append(0x00)
    
    tmp = []
    for i in range(16):
        tmp.append(0)
    
    for i in range(256):
        plaintext = [i]  
        for value in constant:  
            plaintext.append(value)
        
        ctHex = oracle(plaintext, key, numRounds)
        
        ct = []
        for j in range(0, len(ctHex), 2):
            hexPair = ctHex[j:j+2]
            decimalValue = int(hexPair, 16)
            ct.append(decimalValue)
        
        for k in range(16):
            tmp[k] = tmp[k] ^ ct[k]
    
    allZero = True
    for x in tmp:
        if x != 0:
            allZero = False
            break
    
    if allZero:
        return 0
    else:
        return 1


def main():
    num_rounds = int(input(" enter the round "))
    plaintext_hex = "3243f6a8885a308d313198a2e0370734"
    key_hex = "2b7e151628aed2a6abf7158809cf4f3c"
    key_list =  resolve_ketype(key_hex)
    plaintext_list = resolve_plaintext(plaintext_hex)
    output =  AES_encrypt(plaintext_list , key_list, num_rounds)
    print("This is the ciphertext below ")    
    print(output)
    rebit = distinguishingAttack(AES_encrypt ,key_list, num_rounds)
    if rebit == 0:
        
        print(rebit,">>AES reduced round detected.")
    else:
        
        print(rebit,">>Random permutation detected.")
        

main()
