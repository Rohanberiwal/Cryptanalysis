K = [
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
        0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
        0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
        0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
        0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432a97,  0xab9423a7, 0xfc93a039,
        0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
    ]
    
s = [
        7,12,17,22,7,12,17,22,7,12,17,22,7,12,17,22,
        5,9,14,20,5,9,14,20,5,9,14,20,5,9,14,20,
        4,11,16,23,4,11,16,23,4,11,16,23,4,11,16,23,
        6,10,15,21,6,10,15,21,6,10,15,21,6,10,15,21
    ]
    

def leftrotate(x, c):
    x = x & 0xFFFFFFFF
    left_shifted = x << c
    right_shifted = x >> (32 - c)
    result = (left_shifted | right_shifted) & 0xFFFFFFFF
    return result

def int_to_bytes(n, length):
    result = bytearray()
    for counts in range(length):
        result.append(n & 0xFF)
        n >>= 8
    return bytes(result)

def pad_message(message_bytes):
    size  = len(message_bytes) * 8
    message_bytes += b'\x80'
    while (len(message_bytes) % 64) != 56:
        message_bytes += b'\x00'
    message_bytes = message_bytes + int_to_bytes(size, 8)
    return message_bytes

def process_chunk(chunk, A, B, C, D, K, s):
    M = []
    for i in range(16):
        j = i * 4
        m_val = 0
        for k in range(4):
            m_val |= chunk[j + k] << (8 * k)
        M.append(m_val)
    a, b, c, d = A, B, C, D
    for i in range(64):
        if i < 16:
            F = (b & c) | ((~b) & d)
            g = i
        elif i < 32:
            F = (d & b) | ((~d) & c)
            g = (5 * i + 1) % 16
        elif i < 48:
            F = b ^ c ^ d
            g = (3 * i + 5) % 16
        else:
            F = c ^ (b | (~d))
            g = (7 * i) % 16
        temp = d
        d = c
        c = b
        a_plus_F = (a + F + K[i] + M[g]) & 0xFFFFFFFF
        b = (b + leftrotate(a_plus_F, s[i])) & 0xFFFFFFFF
        a = temp
    A = (A + a) & 0xFFFFFFFF
    B = (B + b) & 0xFFFFFFFF
    C = (C + c) & 0xFFFFFFFF
    D = (D + d) & 0xFFFFFFFF
    return A, B, C, D

def to_hex(n):
    hex_str = ''
    for i in range(4):
        shift_amount = i * 8
        shifted_value = n >> shift_amount
        byte_value = shifted_value & 0xFF
        hex_byte = '{:02x}'.format(byte_value)
        hex_str += hex_byte
    return hex_str


def md5(message):        
    A = 0x67452301
    B = 0xefcdab89
    C = 0x98badcfe
    D = 0x10325476
    if isinstance(message, str):
        message = message.encode('utf-8')
    message = pad_message(message)    
    for offset in range(0, len(message), 64):
        chunk = message[offset:offset+64]
        A, B, C, D = process_chunk(chunk, A, B, C, D, K, s)
    hashedresult = to_hex(A) + to_hex(B) + to_hex(C) + to_hex(D)
    return hashedresult

def display_results():
    test_inputs = [
        "", 
        "a", 
        "rohan", 
        "Cryptography", 
        "I love topic in cryptanalysis course  ",
        "Bye bye "
    ]
    results = []
    for inp in test_inputs:
        digest = md5(inp)
        results.append((inp, digest))
    return results

def print_table(results):
    col_width = max(len(inp) for inp, _ in results) + 2
    header = f"{'Input'.ljust(col_width)} | MD5 Digest"
    separator = "-" * (len(header) + 2)
    print(separator)
    print(header)
    print(separator)
    for inp, digest in results:
        print(f"{inp.ljust(col_width)} | {digest}")
    print(separator)

def main():
    results = display_results()
    print_table(results)


main()
