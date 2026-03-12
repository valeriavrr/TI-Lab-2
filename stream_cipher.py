from bitarray import bitarray

class StreamCipher:
    def __init__(self):
        self.bit_register = None
        self.bit_key = None
        self.plain_text = None
        self.cipher_bit = None

    def produce_bit_register(self, parsing_string):
        self.bit_register = bitarray(parsing_string)

    def produce_bit_key(self, length):
        self.bit_key = bitarray(endian='little')
        leng = len(self.bit_register)
        for _ in range(length):
            self.bit_key.append(self.bit_register[0])
            # Полином для регистра длиной 25 бит: x^25 + x^3 + 1
            next_value = self.bit_register[leng - 1 - 24] ^ self.bit_register[leng - 1 - 2]
            self.bit_register.pop(0)
            self.bit_register.append(next_value)

    def cipher(self):
        self.cipher_bit = self.bit_key ^ self.plain_text