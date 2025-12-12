class TrieNode:
    """
    Trie ağacının her bir düğümü.
    Her düğüm bir harfi temsil eder ve çocuklarını (sonraki harfleri) bilir.
    """
    def __init__(self):
        self.children = {}  # Sözlük: { 'a': Node, 'b': Node ... }
        self.code = -1      # Eğer bu düğüm sözlükte bir kelimeyse, kodu burada saklanır.

class LZWTrie:
    def __init__(self):
        self.root = TrieNode()
        self.next_code = 256

    def init_dictionary(self):
        """
        Sözlüğü (Trie Ağacını) ASCII karakterlerle doldurur.
        """
        self.root = TrieNode()
        self.next_code = 256
        
        # 0-255 arasındaki tüm karakterleri kök düğüme ekle
        for i in range(256):
            char = chr(i)
            new_node = TrieNode()
            new_node.code = i
            self.root.children[char] = new_node

    def compress(self, uncompressed_text):
        """
        Trie kullanarak sıkıştırma işlemi.
        Burada Python 'dict' yerine ağaçta (node'lar arasında) gezineceğiz.
        """
        self.init_dictionary()
        compressed_result = []
        
        # Algoritma 'root'tan değil, ilk karakterin olduğu yerden başlar
        # Ancak mantığı basitleştirmek için şöyle yapıyoruz:
        # current_node: Şu an elimizdeki eşleşen en uzun string'in bulunduğu düğüm.
        
        if not uncompressed_text:
            return []

        # İlk karakteri işle (Başlangıç durumu)
        # LZW mantığı: P (current_string) ile başlarız.
        first_char = uncompressed_text[0]
        current_node = self.root.children[first_char]
        
        # İkinci karakterden itibaren döngüye gir
        for char in uncompressed_text[1:]:
            # Ağaçta 'char' yoluna gitmeye çalış (P + C var mı?)
            if char in current_node.children:
                # VARSA: Daha derine in (Longest Prefix Match) 
                current_node = current_node.children[char]
            else:
                # YOKSA:
                # 1. Şu anki düğümün kodunu çıktı ver
                compressed_result.append(current_node.code)
                
                # 2. Yeni yolu (P + C) ağaca ekle
                new_node = TrieNode()
                new_node.code = self.next_code
                self.next_code += 1
                current_node.children[char] = new_node
                
                # 3. Yeni başlangıç noktasına geç (Sadece 'char')
                current_node = self.root.children[char]
        
        # Döngü bittiğinde son kalan düğümün kodunu ekle
        compressed_result.append(current_node.code)
        
        return compressed_result

    def decompress(self, compressed_codes):
        """
        Decompression işlemi Task 1 ile aynıdır (Array kullanılır).
        Trie burada kullanılmaz çünkü elimizde 'Kod' var, 'String'e gitmek istiyoruz.
        """
        # Dictionary: Code (int) -> String
        dictionary = {}
        for i in range(256):
            dictionary[i] = chr(i)
        
        next_code = 256
        result_text = ""

        if not compressed_codes:
            return ""

        previous_code = compressed_codes[0]
        current_string = dictionary[previous_code]
        result_text += current_string

        for current_code in compressed_codes[1:]:
            if current_code in dictionary:
                current_string = dictionary[current_code]
            elif current_code == next_code:
                previous_string = dictionary[previous_code]
                current_string = previous_string + previous_string[0]
            else:
                raise ValueError("Bad compressed code")

            result_text += current_string

            previous_string = dictionary[previous_code]
            new_entry = previous_string + current_string[0]
            
            dictionary[next_code] = new_entry
            next_code += 1
            previous_code = current_code

        return result_text

# Test Bloğu
if __name__ == "__main__":
    lzw = LZWTrie()
    input_text = "TOBEORNOTTOBEORTOBEORNOT"
    print(f"Original: {input_text}")
    
    compressed = lzw.compress(input_text)
    print(f"Compressed Codes: {compressed}")
    
    decompressed = lzw.decompress(compressed)
    print(f"Decompressed: {decompressed}")
    
    if input_text == decompressed:
        print("SUCCESS: Trie-based LZW works!")
    else:
        print("FAIL: Mismatch.")