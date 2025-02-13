import time
import numpy as np

# Define the S-box and its inverse
S_BOX = {
    0x0: 0x6, 0x1: 0x4, 0x2: 0xC, 0x3: 0x5,
    0x4: 0x0, 0x5: 0x7, 0x6: 0x2, 0x7: 0xE,
    0x8: 0x1, 0x9: 0xF, 0xA: 0x3, 0xB: 0xD,
    0xC: 0x8, 0xD: 0xA, 0xE: 0x9, 0xF: 0xB
}

S_INV = {v: k for k, v in S_BOX.items()}  # Inverse S-box

# Permutation P[]
P = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]

def apply_sbox(value):
    """Apply the S-box on a 16-bit value."""
    high_nibble1 = S_BOX[(value >> 12) & 0xF] << 12
    high_nibble2 = S_BOX[(value >> 8) & 0xF] << 8
    low_nibble1 = S_BOX[(value >> 4) & 0xF] << 4
    low_nibble2 = S_BOX[value & 0xF]
    return high_nibble1 | high_nibble2 | low_nibble1 | low_nibble2

def apply_inverse_sbox(value):
    """Apply the inverse S-box."""
    high_nibble1 = S_INV[(value >> 12) & 0xF] << 12
    high_nibble2 = S_INV[(value >> 8) & 0xF] << 8
    low_nibble1 = S_INV[(value >> 4) & 0xF] << 4
    low_nibble2 = S_INV[value & 0xF]
    return high_nibble1 | high_nibble2 | low_nibble1 | low_nibble2

def permute_bits(value):
    """Apply the permutation P."""
    permuted = 0
    for i in range(16):
        if value & (1 << i):
            permuted |= (1 << P[i])
    return permuted

def encrypt(plaintext, round_keys):
    """Encrypt 5-round Toy Cipher."""
    u = plaintext
    for i in range(4):
        a = u ^ round_keys[i]
        s = apply_sbox(a)
        u = permute_bits(s)
    a = u ^ round_keys[4]
    s = apply_sbox(a)
    ciphertext = s ^ round_keys[5]
    return ciphertext

def generate_plaintext_pairs(num_pairs, delta_x):
    """Generate plaintext pairs (m, m') with a fixed difference Δ(x)."""
    plaintext_pairs = []
    for _ in range(num_pairs):
        m = np.random.randint(0, 2**16)
        m_prime = m ^ delta_x
        plaintext_pairs.append((m, m_prime))
    return plaintext_pairs

def filter_ciphertext_pairs(ciphertext_pairs):
    """Filter out invalid ciphertext pairs based on difference propagation."""
    valid_differences = {0x0001, 0x0002, 0x0009, 0x000A}  # From DDT of S-box
    filtered_pairs = [(c1, c2) for c1, c2 in ciphertext_pairs if (c1 ^ c2) & 0x000F in valid_differences]
    return filtered_pairs

def recover_last_round_key(ciphertext_pairs):
    """Brute-force the last-round key using differential cryptanalysis."""
    key_counters = np.zeros(2**16, dtype=int)  # 16-bit key space

    for k_r in range(2**16):  # Try all possible last-round keys
        for c, c_prime in ciphertext_pairs:
            v = apply_inverse_sbox(c ^ k_r)
            v_prime = apply_inverse_sbox(c_prime ^ k_r)
            if (v ^ v_prime) == 0x0002:  # Check against Δ(y)
                key_counters[k_r] += 1

    best_key = np.argmax(key_counters)
    return best_key, key_counters[best_key]

def main():
    round_keys = [0x1111, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666]
    delta_x = 0x0002  
    num_pairs = 2**12
    plaintext_pairs = generate_plaintext_pairs(num_pairs, delta_x)

    ciphertext_pairs = [(encrypt(m, round_keys), encrypt(m_prime, round_keys)) for m, m_prime in plaintext_pairs]

    filtered_pairs = filter_ciphertext_pairs(ciphertext_pairs)

    recovered_key, count = recover_last_round_key(filtered_pairs)

    print(f"Recovered last round key: {hex(recovered_key)} with {count} valid pairs")
    print(f"Actual last round key: {hex(round_keys[5])}")

if __name__ == "__main__":
    main()
