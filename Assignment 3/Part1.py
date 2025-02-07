S = [6, 4, 12, 5, 0, 7, 2, 14, 1, 15, 3, 13, 8, 10, 9, 11]
P = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]

def toy_cipher_encrypt(m, round_keys):
    u = m
    r = 5

    for i in range(1, r):
        a = u ^ round_keys[i - 1]
        A0, A1, A2, A3 = (a >> 12) & 0xF, (a >> 8) & 0xF, (a >> 4) & 0xF, a & 0xF
        S_output = (S[A0] << 12) | (S[A1] << 8) | (S[A2] << 4) | S[A3]
        y = S_output
        permuted_y = 0
        for j in range(16):
            permuted_y |= ((y >> j) & 1) << P[j]
        u = permuted_y

    a = u ^ round_keys[r - 1]
    A0, A1, A2, A3 = (a >> 12) & 0xF, (a >> 8) & 0xF, (a >> 4) & 0xF, a & 0xF
    S_output = (S[A0] << 12) | (S[A1] << 8) | (S[A2] << 4) | S[A3]
    y = S_output
    ciphertext = y ^ round_keys[r - 1]
    return ciphertext

message = 0x1234
round_keys = [0x1111, 0x2222, 0x3333, 0x4444, 0x5555]  
ciphertext = toy_cipher_encrypt(message, round_keys)
print(f"Ciphertext: {ciphertext:016x}")
