#!/usr/bin/env python3
def permute(block, table):
    return [block[x - 1] for x in table]

def left_shift(bits, n):
    return bits[n:] + bits[:n]

def xor(bits1, bits2):
    return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]

def int_to_bits(val, bits):
    return [int(b) for b in bin(val)[2:].rjust(bits, '0')]

def bits_to_int(bits):
    return int("".join(str(b) for b in bits), 2)

def hex_to_bits(hex_string):
    hex_string = hex_string.strip().replace(" ", "")
    bits = []
    for ch in hex_string:
        bits.extend(int_to_bits(int(ch, 16), 4))
    return bits

def bits_to_hex(bits):
    hex_string = ""
    for i in range(0, len(bits), 4):
        nibble = bits[i:i + 4]
        hex_string += format(bits_to_int(nibble), 'x')
    return hex_string.upper()

# DES Tables
IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

FP = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

S_BOX = [
    [
        [14, 4,  13, 1,  2, 15, 11, 8,  3, 10, 6, 12, 5, 9,  0, 7],
        [0,  15, 7,  4,  14, 2,  13, 1,  10, 6, 12, 11, 9, 5,  3, 8],
        [4,  1,  14, 8,  13, 6,  2,  11, 15, 12, 9, 7,  3, 10, 5, 0],
        [15, 12, 8,  2,  4,  9,  1,  7,  5, 11, 3, 14, 10, 0, 6, 13]
    ],
    [
        [15, 1,  8, 14, 6, 11, 3, 4,  9, 7, 2, 13, 12, 0, 5, 10],
        [3,  13, 4, 7,  15, 2,  8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0,  14, 7, 11, 10, 4,  13, 1,  5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8,  10, 1,  3, 15, 4, 2,  11, 6, 7, 12, 0, 5, 14, 9]
    ],
    [
        [10, 0,  9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7,  0, 9,  3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6,  4, 9,  8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1,  10, 13, 0,  6, 9, 8, 7,  4, 15, 14, 3, 11, 5, 2, 12]
    ],
    [
        [7,  13, 14, 3,  0, 6,  9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8,  11, 5,  6, 15, 0, 3,  4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6,  9, 0,  12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3,  15, 0, 6,  10, 1,  13, 8,  9, 4, 5, 11, 12, 7, 2, 14]
    ],
    [
        [2,  12, 4,  1,  7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2,  12, 4, 7,  13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4,  2,  1,  11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8,  12, 7,  1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    ],
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    ],
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    ],
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    ]
]

P = [
    16, 7, 20, 21,
    29, 12, 28, 17,
    1, 15, 23, 26,
    5, 18, 31, 10,
    2, 8, 24, 14,
    32, 27, 3, 9,
    19, 13, 30, 6,
    22, 11, 4, 25
]

PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2,
                  1, 2, 2, 2, 2, 2, 2, 1]

def generate_round_keys(key_bits):
    key56 = permute(key_bits, PC1)
    C = key56[:28]
    D = key56[28:]
    round_keys = []
    for shift in SHIFT_SCHEDULE:
        C = left_shift(C, shift)
        D = left_shift(D, shift)
        combined = C + D
        round_keys.append(permute(combined, PC2))
    return round_keys

def sbox_substitution(expanded_half):
    output = []
    for i in range(8):
        block = expanded_half[i * 6:(i + 1) * 6]
        row = (block[0] << 1) | block[5]
        column = (block[1] << 3) | (block[2] << 2) | (block[3] << 1) | block[4]
        s_val = S_BOX[i][row][column]
        output.extend(int_to_bits(s_val, 4))
    return output

def round_function(R, round_key, debug=False):
    expanded_R = permute(R, E)
    if debug:
        print("    Expanded R:       ", bits_to_hex(expanded_R))
    xored = xor(expanded_R, round_key)
    if debug:
        print("    XOR with key:     ", bits_to_hex(xored))
    sboxed = sbox_substitution(xored)
    if debug:
        print("    S-box output:     ", bits_to_hex(sboxed))
    f_out = permute(sboxed, P)
    if debug:
        print("    f(R, K) output:   ", bits_to_hex(f_out))
    return f_out

def des_encrypt_hex_block(plaintext_hex, key_hex, debug_rounds=False):
    plaintext_bits = hex_to_bits(plaintext_hex)
    key_bits = hex_to_bits(key_hex)
    round_keys = generate_round_keys(key_bits)
    permuted_bits = permute(plaintext_bits, IP)
    print("    permuted key :   ", permuted_bits)
    L = permuted_bits[:32]
    R = permuted_bits[32:]
    for i in range(16):
        print(f"Round {i+1}:")
        print("  L:                  ", bits_to_hex(L))
        print("  R:                  ", bits_to_hex(R))
        print("  Round Key:          ", bits_to_hex(round_keys[i]))
        f_out = round_function(R, round_keys[i], debug=debug_rounds)
        temp_R = R.copy()
        R = xor(L, f_out)
        L = temp_R
        print("  New L:              ", bits_to_hex(L))
        print("  New R:              ", bits_to_hex(R))
        print("-" * 50)
    combined = R + L
    final_bits = permute(combined, FP)
    return bits_to_hex(final_bits)

def remove_padding(hex_str):
    pad_byte = int(hex_str[-2:], 16)  # Check the last byte for padding size
    return hex_str[:-2*pad_byte]  # Remove padding


def pad_plaintext_hex(plaintext_hex):
    hex_str = plaintext_hex.strip().replace(" ", "")
    if len(hex_str) % 2 != 0:
        raise ValueError("Plaintext hex must have an even number of digits.")
    byte_len = len(hex_str) // 2
    block_size = 8  # DES block size in bytes
    if byte_len % block_size == 0:
        return hex_str  # No padding needed if it's already aligned
    else:
        pad_bytes = block_size - (byte_len % block_size)
        pad_value = format(pad_bytes, '02X')
        return hex_str + pad_value * pad_bytes


"""
# Modified padding function: apply padding only if plaintext is not a multiple of 8 bytes.
def pad_plaintext_hex(plaintext_hex):
    hex_str = plaintext_hex.strip().replace(" ", "")
    if len(hex_str) % 2 != 0:
        raise ValueError("Plaintext hex must have an even number of digits.")
    byte_len = len(hex_str) // 2
    block_size = 8  # DES block size in bytes
    if byte_len % block_size == 0:
        # If plaintext is already a multiple of block size, return unchanged.
        return hex_str
    else:
        pad_bytes = block_size - (byte_len % block_size)
        pad_value = format(pad_bytes, '02X')
        return hex_str + pad_value * pad_bytes
"""
def des_encrypt_ecb(plaintext_hex, key_hex, debug_rounds=False):
    padded = pad_plaintext_hex(plaintext_hex)
    ciphertext = ""
    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        ciphertext += des_encrypt_hex_block(block, key_hex, debug_rounds=debug_rounds)
    return ciphertext, len(padded) // 2


def des_decrypt_hex_block(ciphertext_hex, key_hex, debug_rounds=False):
    ciphertext_bits = hex_to_bits(ciphertext_hex)
    key_bits = hex_to_bits(key_hex)
    round_keys = generate_round_keys(key_bits)
    permuted_bits = permute(ciphertext_bits, IP)
    L = permuted_bits[:32]
    R = permuted_bits[32:]
    for i in range(15, -1, -1):
        print(f"Round {16 - i}:")
        print("  L:                  ", bits_to_hex(L))
        print("  R:                  ", bits_to_hex(R))
        print("  Round Key:          ", bits_to_hex(round_keys[i]))
        f_out = round_function(R, round_keys[i], debug=debug_rounds)
        temp_R = R.copy()
        R = xor(L, f_out)
        L = temp_R
        print("  New L:              ", bits_to_hex(L))
        print("  New R:              ", bits_to_hex(R))
        print("-" * 50)
    combined = R + L
    final_bits = permute(combined, FP)
    return bits_to_hex(final_bits)

def des_decrypt_ecb(ciphertext_hex, key_hex, debug_rounds=False):
    ciphertext = ciphertext_hex.strip().replace(" ", "")
    plaintext = ""
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        plaintext += des_decrypt_hex_block(block, key_hex, debug_rounds=debug_rounds)
    return plaintext, len(ciphertext) // 2


def main():
    test_cases = [
        ("123456ABCD132536", "AABB09182736CCDD"),
        ("FFFFFFFFFFFFFFFF", "0000000000000000"),
        ("1122334455667788", "8877665544332211"),
        ("A1B2C3D4E5F60789", "89F607E5D4C3B2A1"),
        ("0001020304050607", "08090A0B0C0D0E0F"),
        ("ABCDEF1234567890", "1234567890ABCDEF"),
        ("DEADBEEFCAFEBABE", "BABECAFEF00DDEAD"),
        ("0011223344556677", "7766554433221100"),
        ("AABBCCDDEEFF0011", "1100FFEEDDCCBBAA"),
        ("1020304050607080", "8090706050403020"),
        ("13579BDF02468ACE", "CE8A6420FDB97531"),
        ("ABC123ABC123ABC1", "C1ABC123ABC123AB"),
        ("1122446688AABBCC", "CCBBAA8866442211"),
        ("5566778899AABBCC", "CCDDBBAA99887766"),
        ("9988776655443322", "2233445566778899"),
        ("A0B1C2D3E4F5A6B7", "B7A6F5E4D3C2B1A0"),
        ("0F1E2D3C4B5A6978", "78695A4B3C2D1E0F"),
        ("ABCDEFABCDEFABCD", "DCBAFEDCBAFEDCBA"),
        ("1234432112344321", "4321123443211234"),
        ("BEEFDEADBEEFDEAD", "DEADBEEFDEADBEEF")
    ]
    
    for i, (plaintext, key) in enumerate(test_cases):
        print(f"Test Case {i+1}")
        print("-" * 50)
        plaintext_hex = plaintext
        key_hex = key
        
        padded_plaintext = pad_plaintext_hex(plaintext_hex)
        print("Plaintext (hex):", plaintext_hex)
        print("Padded Plaintext (hex):", padded_plaintext)
        print("Key (hex):", key_hex)
        print("=" * 50)
        
        ciphertext, ct_bytes = des_encrypt_ecb(plaintext_hex, key_hex, debug_rounds=True)
        pt_bytes = len(padded_plaintext) // 2
        print("=" * 50)
        print("Ciphertext (hex):", ciphertext)
        print("Plaintext Bytes:", pt_bytes)
        print("Ciphertext Bytes:", ct_bytes)
        decrypted_text, pt_bytes = des_decrypt_ecb(ciphertext , key_hex, debug_rounds=True)
        
        print("=" * 50)
        print("Ciphertext (hex):", ciphertext)
        print("Decrypted Plaintext (hex):", decrypted_text)
        print("Plaintext Bytes:", pt_bytes)
        decrypted_plaintext = remove_padding(decrypted_text)
        print("Decrypted Plaintext (without padding):", decrypted_plaintext)
        print("\n" + "#" * 60 + "\n")
        
if __name__ == "__main__":
    main()
