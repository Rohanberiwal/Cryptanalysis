import math
INIT_VALUES = (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)
round1 = [7, 12, 17, 22]
round1_shifts = round1 * 4
round2 = [5, 9, 14, 20]
round2_shifts = round2 * 4
round3 = [4, 11, 16, 23]
round3_shifts = round3 * 4
round4 = [6, 10, 15, 21]
round4_shifts = round4 * 4
SHIFT_AMOUNTS = round1_shifts + round2_shifts + round3_shifts + round4_shifts

round1_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
round2_indices = [
    1, 6, 11, 0,
    5, 10, 15, 4,
    9, 14, 3, 8,
    13, 2, 7, 12
]
round3_indices = [
    5, 8, 11, 14,
    1, 4, 7, 10,
    13, 0, 3, 6,
    9, 12, 15, 2
]
round4_indices = [
    0, 7, 14, 5,
    12, 3, 10, 1,
    8, 15, 6, 13,
    4, 11, 2, 9
]
INDEX_ORDER = round1_indices + round2_indices + round3_indices + round4_indices

T_VALUES = []
for i in range(64):
    angle = i + 1
    sine_value = math.sin(angle)
    absolute_sine = abs(sine_value)
    scaled_value = absolute_sine * (2 ** 32)
    integer_value = int(scaled_value)
    final_value = integer_value & 0xFFFFFFFF
    T_VALUES.append(final_value)

def F(x, y, z): 
    return (x & y) | (~x & z)

def G(x, y, z): 
    return (x & z) | (y & ~z)

def H(x, y, z): 
    return x ^ y ^ z

def I(x, y, z): 
    return y ^ (x | ~z)

FUNC_LIST = []
for i in range(64):
    if i < 16:
        FUNC_LIST.append(F)
    elif i < 32:
        FUNC_LIST.append(G)
    elif i < 48:
        FUNC_LIST.append(H)
    else:
        FUNC_LIST.append(I)

def left_rotate(x, amount):
    x = x & 0xFFFFFFFF
    left_shifted = (x << amount) & 0xFFFFFFFF
    right_shifted = x >> (32 - amount)
    combined = left_shifted | right_shifted
    result = combined & 0xFFFFFFFF
    return result

def padding(message):
    original_length = len(message) * 8
    message += b'\x80'    
    while (len(message) % 64) != 56:
        message += b'\x00'    
    length_bytes = original_length.to_bytes(8, byteorder='little')
    message += length_bytes
    return message

def process_chunk(chunk, a, b, c, d):
    X = []
    for i in range(0, 64, 4):
        word = chunk[i:i+4]
        word_int = int.from_bytes(word, byteorder='little')
        X.append(word_int)
    for i in range(64):
        func_result = FUNC_LIST[i](b, c, d)
        temp_a = a
        temp_t = T_VALUES[i]
        temp_x = X[INDEX_ORDER[i]]
        temp_shift = SHIFT_AMOUNTS[i]
        sum_parts = func_result + temp_a
        sum_parts = (sum_parts + temp_t) & 0xFFFFFFFF
        sum_parts = (sum_parts + temp_x) & 0xFFFFFFFF
        rotated = left_rotate(sum_parts, temp_shift)
        new_b = (b + rotated) & 0xFFFFFFFF
        a, b, c, d = d, new_b, b, c
    return a, b, c, d

def md5_output(message):
    try:
        message = message.encode()
    except AttributeError:
        pass
    message = padding(message)
    return compute_md5_hash(message)


def compute_md5_hash(message):
    A, B, C, D = INIT_VALUES
    for i in range(0, len(message), 64):
        chunk = message[i:i+64]
        a, b, c, d = process_chunk(chunk, A, B, C, D)
        A = (A + a) & 0xFFFFFFFF
        B = (B + b) & 0xFFFFFFFF
        C = (C + c) & 0xFFFFFFFF
        D = (D + d) & 0xFFFFFFFF
    return format_output(A, B, C, D)

def format_output(A, B, C, D):
    parts = [A, B, C, D]
    result = ''
    for x in parts:
        byte_value = x.to_bytes(4, byteorder='little')
        hex_value = byte_value.hex()
        result += hex_value
    return result

def test_md5():
    test_cases = [
        "",
        "a",
        "abc",
        "message digest",
        "abcdefghijklmnopqrstuvwxyz",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
        "12345678901234567890123456789012345678901234567890123456789012345678901234567890"
    ]
    for testing in test_cases:
        result = md5_output(testing)
        print(f'MD5 ("{testing}") = {result}')

test_md5()
