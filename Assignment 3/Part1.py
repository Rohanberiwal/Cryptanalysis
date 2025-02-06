import random

S_BOX = [0x6, 0x4, 0xC, 0x5, 0x0, 0x7, 0x2, 0xE, 0x1, 0xF, 0x3, 0xD, 0x8, 0xA, 0x9, 0xB]
P = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]

def substitute(nibble):
    return S_BOX[nibble]

def permute(bits):
    return [bits[P[i]] for i in range(16)]

def to_bits(val, size=16):
    return [(val >> i) & 1 for i in range(size - 1, -1, -1)]

def from_bits(bits):
    return sum(b << (15 - i) for i, b in enumerate(bits))


def encrypt(plaintext, round_keys):
    state = plaintext
    for i in range(len(round_keys) - 1):
        state ^= round_keys[i]
        state_nibbles = [(state >> (4 * j)) & 0xF for j in range(4)][::-1]
        state_nibbles = [substitute(n) for n in state_nibbles]
        state_bits = to_bits(sum(n << (4 * j) for j, n in enumerate(state_nibbles)))
        state_bits = permute(state_bits)
        state = from_bits(state_bits)

    state ^= round_keys[-1]
    state_nibbles = [(state >> (4 * j)) & 0xF for j in range(4)][::-1]
    state_nibbles = [substitute(n) for n in state_nibbles]
    state = sum(n << (4 * j) for j, n in enumerate(state_nibbles))
    
    return state ^ round_keys[-1]

plaintext = 0x1234
round_keys = [0x1111, 0x2222, 0x3333, 0x4444, 0x5555]
ciphertext = encrypt(plaintext, round_keys)
print(f"Ciphertext: {ciphertext:04X}")
