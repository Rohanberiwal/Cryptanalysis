import random
from hashlib import sha256

def E(K, P):
    return int(sha256((str(K) + str(P)).encode()).hexdigest(), 16)

def precompute_chains(m, t, P):
    chains = []
    print(f"Starting precomputation with {m} chains of length {t}...")
    for i in range(m):
        if i % (m // 10) == 0:
            print(f"Precomputing chain {i}/{m}...")
        SP = random.getrandbits(64)
        chain = [SP]
        K = SP
        for _ in range(t - 1):
            K = E(K, P)
            chain.append(K)
        EP = chain[-1]
        chains.append((SP, EP))
    print("Precomputation completed.")
    return chains

def search_for_key(chains, P, C, t):
    print("Starting online search...")
    Y = C
    for i in range(t - 1):
        if i % (t // 10) == 0:
            print(f"Searching at step {i}/{t-1}...")
        for j in range(len(chains)):
            if Y == chains[j][1]:
                print(f"Match found in chain {j} at step {i}. Reconstructing chain...")
                SP = chains[j][0]
                K = SP
                for k in range(1, t):
                    K = E(K, P)
                    if K == C:
                        print("Key successfully recovered.")
                        return K
                print("False match; continuing search...")
                break
        Y = E(Y, P)
    print("Key not found.")
    return "Key not found"

def TMTO_attack(m, t, P, C):
    print("Executing Time-Memory Trade-off Attack...")
    chains = precompute_chains(m, t, P)
    recovered_key = search_for_key(chains, P, C, t)
    return recovered_key

if __name__ == "__main__":
    plaintext = [18, 52, 86, 120]
    ciphertext = [86, 116, 35, 75]
    P = int(''.join([str(x) for x in plaintext]), 16)
    C = int(''.join([str(x) for x in ciphertext]), 16)
    m = 2**16
    t = 2**16
    recovered_key = TMTO_attack(m, t, P, C)
    print("Recovered Key:", recovered_key)
