# This is the import statemnet for math lib in python 
import math
# INIT values is a tuple that is use to declare the A ,B,C,D values that are used in the later half of the code
INIT_VALUES = (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)
# The below is the left shift amount that if for four seperate rounds 
# This list round one is hard code and declared 
round1 = [7, 12, 17, 22]
# This is used to make sixteen value for the sixteen operation rounds .
# This is then stored in the roundone shift list
round1_shifts = round1 * 4
# The below is the left shift amount that if for four seperate rounds 
# This list round two is hard code and declared 
round2 = [5, 9, 14, 20]
# This is used to make sixteen value for the sixteen operation rounds .This is for the round two
# This is stored in the shift near the round two
round2_shifts = round2 * 4
# The below is the left shift amount that if for four seperate rounds 
# This list round Three is hard code and declared 
round3 = [4, 11, 16, 23]
# The below is the left shift amount that if for four seperate rounds . This is forr Round three 
# This list round two is hard code and declared 
round3_shifts = round3 * 4
round4 = [6, 10, 15, 21]
round4_shifts = round4 * 4
# The shift amount is use to add all the four round shit and then store in the variable 
# This shift amount is thne used  in the other half of the code and it is a global variable as it must be ascessable in the whole code .
SHIFT_AMOUNTS = round1_shifts + round2_shifts + round3_shifts + round4_shifts

# These are the message word indices used in each of the 16 operations of round 1.
# This index is saved from the index zero to fifteen in the list .  
round1_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
# In round 2, the index is calculated as maths function tht  is (1 + 5 * i) % 16
# This permutation helps diffuse the in the upcoming operation that would be done .  
round2_indices = [
    1, 6, 11, 0,
    5, 10, 15, 4,
    9, 14, 3, 8,
    13, 2, 7, 12
]
# In round 3, the index is calculated as: (5 + 3 * i) % 16
# This helps in the scatter of the messages . can be treasted as a part of the perms .
round3_indices = [
    5, 8, 11, 14,
    1, 4, 7, 10,
    13, 0, 3, 6,
    9, 12, 15, 2
]
# In round 4, the index is calculated as: (7 * i) % 16
# This is the most  pattern of all rounds to maximize diffusion.
round4_indices = [
    0, 7, 14, 5,
    12, 3, 10, 1,
    8, 15, 6, 13,
    4, 11, 2, 9
]
# Complete Index Order for All 64 Operations
# MD5 processes input in 4 rounds of 16 operations each, and this full list combines
# all 64 indices used in those operations, following the MD5 spec.
INDEX_ORDER = round1_indices + round2_indices + round3_indices + round4_indices

#  sin value table or the T value that is use in the whole code  
# These will be the 64 constants (T-values) used in the main MD5 transformation loop.
# Each T[i] is computed as: floor(2^32 × abs(sin(i + 1)))
# These are precomputed to avoid recalculating inside the loop.
T_VALUES = []
# Generates the 64 constant T-values used for the hashing .
# Each T[i] is defined as floor(2^32 × abs(sin(i + 1))).
#These value can also be hardcoded using the same func  
# The sine is calculated in radians, and the result is converted to 32-bit unsigned int.
# This adds non-linearity and ensures a proper uniform oevrall the code.
def generate_t_values():
    global T_VALUES
    for i in range(64):
        angle = i + 1
        sine_value = math.sin(angle)
        absolute_sine = abs(sine_value)
        scaled_value = absolute_sine * (2 ** 32)
        integer_value = int(scaled_value)
        final_value = integer_value & 0xFFFFFFFF
        T_VALUES.append(final_value)

 # This F function Used in Round 1 of MD5. Chooses bits from y or z depending on x.
def F(x, y, z): 
    return (x & y) | (~x & z)
#This G  function Used in Round 2. Chooses bits from x or y depending on z.
def G(x, y, z): 
    return (x & z) | (y & ~z)
# This  H fucntion  used in Round 3. Simple XOR mixing of all three inputs.
def H(x, y, z): 
    return x ^ y ^ z

 #The I function is used in Round 4. A combination of OR, NOT, and XOR for addition of  diffusion.
def I(x, y, z): 
    return y ^ (x | ~z)

# This below is a blend of  (F, G, H, I) used in the 64 steps of MD5.
#There are total of the sixteen roundad in the set .
# Round 1 uses F (0–15), Round 2 uses G (16–31), Round 3 uses H (32–47), Round 4 uses I (48–63).
# This allows the main loop to call the correct function dynamically based on the step.
# The result is stored in the global FUNC_LIST list for use in MD5's main compression loop.
FUNC_LIST = []
def generate_func_list():
    global FUNC_LIST
    for i in range(64):
        if i < 16:
            FUNC_LIST.append(F)
        elif i < 32:
            FUNC_LIST.append(G)
        elif i < 48:
            FUNC_LIST.append(H)
        else:
            FUNC_LIST.append(I)

# Performs a left rotation (Lr) on a 32-bit unsigned integer.
# This operation shifts the bits of x to the left by 'amount' positions,
#Then we have the md mix func that is used to mix that to the right .
#The intermed values are convert to thirty two bit mask.
# This ensures compatibility across different systems .
def left_rotate(x, amount):
    x = x & 0xFFFFFFFF
    left_shifted = (x << amount) & 0xFFFFFFFF
    right_shifted = x >> (32 - amount)
    combined = left_shifted | right_shifted
    result = combined & 0xFFFFFFFF
    return result

# Now we  Pads the input message so as to fit block to a proper size required 
# The padding involves adding a '1' bit (0x80), followed by '0' bits (0x00). This is done for the whole message .
# This ensures the message length is a multiple of 512 bits. Also there a len variable at the end .    
# Takes the input as the message and  returns the padded result variable  . 
def padding(message):
    original_length = len(message) * 8
    message += b'\x80'    
    while (len(message) % 64) != 56:
        message += b'\x00'    
    length_bytes = original_length.to_bytes(8, byteorder='little')
    message += length_bytes
    return message

# Processes a 64-byte chunk of data using the MD5 algorithm's round functions, constants, and shifts.
# The chunk is divided into 16 32-bit words .
# In each of the 64 rounds, a function from FUNC_LIST is used to applied to the current values of b, c, d.
# The corresponding T value from T_VALUES is added, and a word from X is included based on INDEX_ORDER That is mented in the lsit .
# The result is rotated left by a specified number of bits SHIFT_AMOUNTS list and added to b.
# The values of a, b, c, and d are updated in each round .
# The final result is the updated values of a, b, c, and d after number of the rounds are compelted.
# These values are returned at the end, which will be used in the overall hash calculation.
# This function is part of the core MD5 algorithm for processing data in blocks 
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

# Processes the input message to generate an MD5 hash.
# First, it ensures the message is in byte format by encoding .
# The message is then padded to meet the block size requirements of the MD5 algorithm.
# After padding, the message is passed to the `compute_md5_hash` function which computes the MD5 hash.
# The resulting MD5 hash is returned as the output.
def md5_output(message):
    try:
        message = message.encode()
    except AttributeError:
        pass
    message = padding(message)
    return compute_md5_hash(message)

# This func is use to do the MD5 hash for the given input message.
# Initializes the MD5 state variables A, B, C, and D using the predefined initial Init value list.
# The message is processed in 64-byte chunks .
# For each 64-byte chunk, the process_chunk function call is made .
# After the ops , the resulting values of a, b, c, d are added to the current values of A, B, C, D.
# The addition is done with a 32-bit overflow, ensuring that the values are within the MD5 block size limit .
# The final result in A, B, C, and D after processing all chunks of the message.
#  When all the chucnks are being processed, the final MD5 hash is generated by calling the format_output function.
# The format_output function takes the final values of A, B, C, D and formats them into the output format.
# The computed MD5 hash is returned as the final result of the function.
# The result is a 128-bit hash .
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

# cleans the output so as to present it  
# Each of these values (A, B, C, D) is a 32-bit integer, which is converted into 4 bytes.
# The bytes are converted to hexadecimal string using little-endian byte order.
# The individual hex values of A, B, C, and D are joined to return the result  .
# This process converts the 128-bit MD5 hash into a 32  hexadecimal string.
# The output is the hexadecimal string that is converted.
# The result is returned as a single string, which is the MD5 hash of the input message.
def format_output(A, B, C, D):
    parts = [A, B, C, D]
    result = ''
    for x in parts:
        byte_value = x.to_bytes(4, byteorder='little')
        hex_value = byte_value.hex()
        result += hex_value
    return result

# This function tests the MD5 implementation by running several test cases
# The procedure first creates T-values which serve MD5 rounds and generates a function list named FUNC_LIST
#The MD5 algorithm uses T-values derived from the sine function for its constant round-based operations
# FUNC_LIST holds all transforming functions which the MD5 algorithm application uses during each round of its operation.
#  The function displays the values
# The function creates test cases supporting input strings ,
# single characters, small phrases, and larger text inputs
# The test cases enter the `md5_output` function to achieve MD5 hash generation
# n The computed MD5 hash for each test case is printed alongside the original input.
# This helps verify the accuracy and correctness of the MD5 implementation across various inputs
# Single empty strings as well as 128 character strings fall under the test cases' input range
# The goal is to ensure that the MD5 algorithm is working correctly for a variety of inputs.
# The testing procedure must validate the MD5 algorithm operates correctly on numerous input values.
def test_md5():
    generate_t_values()
    generate_func_list()
    print("This is the T values or sine value Tables..")
    print(T_VALUES)
    print("This is the function list ")
    print(FUNC_LIST)
    print()
    print("....Below  is the suite test cases ....")
    print()
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
#This is the func where everything starts 
test_md5()
