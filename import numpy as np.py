import numpy as np

def get_constellation(M):
    return np.arange(-(M - 1), M, 2)

def digital_modulation(bits, M):
    bits = np.array(bits)
    L = int(np.log2(M))  # bits per symbol

    # Pad if needed
    if len(bits) % L != 0:
        bits = np.concatenate([bits, np.zeros(L - len(bits) % L, dtype=int)])

    # Group bits
    bit_groups = bits.reshape(-1, L)
    constellation = get_constellation(M)
    
    symbols = []
    for group in bit_groups:
        binary_str = ''.join(str(b) for b in group)
        index = int(binary_str, 2)
        symbols.append(constellation[index])  # Map index to constellation value

    return np.array(symbols)

bits = [1, 0, 1, 1,1,1,0,1,0,1,0]  # 4 bits → 2 symbols with M=4
symbols = digital_modulation(bits, 4)
print(symbols)



def create_message(symbols, K): 
    return np.repeat(symbols, K)
    

K = 5
m = create_message(symbols, K)
print(m)

def get_symbols(message, K):
    return message[::K]


print(get_symbols(m, K))

import numpy as np

