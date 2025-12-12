class LZW:
    def __init__(self):
        self.dictionary = {}

    def compress(self, uncompressed_text):
        # Initialize dictionary with ASCII values (0-255)
        self.dictionary = {}
        for i in range(256):
            self.dictionary[chr(i)] = i

        current_string = ""
        compressed_result = []
        next_code = 256

        for current_char in uncompressed_text:
            combined_string = current_string + current_char

            if combined_string in self.dictionary:
                # If combined string is found, keep growing the string
                current_string = combined_string
            else:
                # If not found, output the code for the current_string
                compressed_result.append(self.dictionary[current_string])

                # Add the new combination to the dictionary
                self.dictionary[combined_string] = next_code
                next_code += 1

                # Start new string with the current character
                current_string = current_char

        # Append the code for the last remaining string
        if current_string != "":
            compressed_result.append(self.dictionary[current_string])

        return compressed_result

    def decompress(self, compressed_codes):
        # Initialize dictionary with ASCII values (0-255)
        self.dictionary = {}
        for i in range(256):
            self.dictionary[i] = chr(i)
        
        next_code = 256
        result_text = ""

        if not compressed_codes:
            return ""
            
        previous_code = compressed_codes[0]
        current_string = self.dictionary[previous_code]
        result_text += current_string
        
        # Loop through the code
        for current_code in compressed_codes[1:]:
            if current_code in self.dictionary:
                # Normal case: The code is in the dictionary
                current_string = self.dictionary[current_code]
            elif current_code == next_code:
                # Tricky case: The code is NOT in the dictionary yet -> new_string = previous_string + previous_string[0]
                previous_string = self.dictionary[previous_code]
                current_string = previous_string + previous_string[0]
            else:
                raise ValueError("Bad compressed code")

            result_text += current_string

            # Add new entry to dictionary
            # Entry = previous_string + first_char_of_current_string
            previous_string = self.dictionary[previous_code]
            new_entry = previous_string + current_string[0]
            
            self.dictionary[next_code] = new_entry
            next_code += 1

            previous_code = current_code

        return result_text

# TEST KISMI
if __name__ == "__main__":
    lzw = LZW()
    
    input_text = "ABABABA"
    print(f"Original: {input_text}")
    
    compressed = lzw.compress(input_text)
    print(f"Compressed Codes: {compressed}")
    
    decompressed = lzw.decompress(compressed)
    print(f"Decompressed: {decompressed}")
    
    if input_text == decompressed:
        print("SUCCESS: Original and Decompressed match exactly!")
    else:
        print("ERROR: Mismatch!")