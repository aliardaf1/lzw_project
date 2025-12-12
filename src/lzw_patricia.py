class PatriciaNode:
    def __init__(self, label="", code=-1):
        self.label = label      # Bu düğüme gelen kenarın üzerindeki yazı (Örn: "ple")
        self.code = code        # Eğer burası bir kelime sonuysa kodu (Örn: 256)
        self.children = {}      # Çocuklar: { 'a': Node, 'b': Node ... }

class LZWPatricia:
    def __init__(self):
        self.root = PatriciaNode()
        self.next_code = 256

    def init_dictionary(self):
        self.root = PatriciaNode()
        self.next_code = 256
        for i in range(256):
            char = chr(i)
            # ASCII karakterleri root'a doğrudan ekle
            self.root.children[char] = PatriciaNode(label=char, code=i)

    def search(self, string):
        """
        Verilen string sözlükte var mı diye arar.
        Varsa kodunu, yoksa -1 döner.
        """
        current_node = self.root
        idx = 0  # String üzerinde nerede olduğumuz
        
        while idx < len(string):
            char = string[idx]
            
            if char not in current_node.children:
                return -1
            
            child = current_node.children[char]
            label = child.label
            
            # Kenar üzerindeki label ile stringin geri kalanını kıyasla
            
            match_len = 0
            while match_len < len(label) and (idx + match_len) < len(string):
                if label[match_len] != string[idx + match_len]:
                    break 
                match_len += 1
            
            if match_len == len(label):
                # Kenarın tamamı eşleşti, düğüme in ve devam et
                idx += match_len
                current_node = child
            else:
                # Kenarın sadece bir kısmı eşleşti veya label aranan stringden daha uzun
                # Tam eşleşme yok demektir.
                return -1
    
        # Son geldiğimiz düğümün geçerli bir kodu var mı?
        if current_node.code != -1:
            return current_node.code
        return -1

    def insert(self, string, code):
        """
        Eklemek istediğimiz string'i patricia tree'ye ekler.
        """
        current_node = self.root
        idx = 0
        
        while idx < len(string):
            char = string[idx]
            
            # DURUM 1: Hiç böyle bir yol yok. Yeni dal ekle.
            if char not in current_node.children:
                remaining_string = string[idx:]
                current_node.children[char] = PatriciaNode(label=remaining_string, code=code)
                return

            child = current_node.children[char]
            label = child.label
            
            # Label ile stringi karşılaştır
            match_len = 0
            while match_len < len(label) and (idx + match_len) < len(string):
                if label[match_len] != string[idx + match_len]:
                    break
                match_len += 1
            
            # DURUM 2: Kenarın tamamı eşleşti
            if match_len == len(label):
                idx += match_len
                current_node = child
                # Eğer string burada bittiyse, kodu ata
                if idx == len(string):
                    if current_node.code == -1:
                        current_node.code = code
                    return
            
            # DURUM 3: Kenarın ortasında uyuşmazlık (SPLIT GEREKİYOR) 
            else:
                # Mevcut 'child' düğümünü ikiye böleceğiz.
                # Ortak kısım (prefix): label[:match_len]
                # Kalan eski kısım (suffix): label[match_len:]
                
                common_prefix = label[:match_len]
                old_suffix = label[match_len:]
                remaining_new_string = string[idx + match_len:]
                
                child.label = common_prefix
            
                
                # Eski yapıyı temsil edecek yeni düğüm
                new_split_child = PatriciaNode(label=old_suffix, code=child.code)
                new_split_child.children = child.children # Eski çocuğun çocuklarını alır
                
                child.children = {} 
                child.code = -1
                
                child.children[old_suffix[0]] = new_split_child
                
                #  yeni eklenen yolu bağla
                if remaining_new_string:
                    new_leaf = PatriciaNode(label=remaining_new_string, code=code)
                    child.children[remaining_new_string[0]] = new_leaf
                else:
                    # Eğer yeni kelime tam burada bitiyorsa
                    child.code = code
                
                return

    def compress(self, uncompressed_text):

        self.init_dictionary()
        compressed_result = []
        
        current_string = ""
        
        for char in uncompressed_text:
            combined_string = current_string + char
            
            code = self.search(combined_string)
            
            if code != -1:
                current_string = combined_string
            else:
                prefix_code = self.search(current_string)
                compressed_result.append(prefix_code)
                
                self.insert(combined_string, self.next_code)
                self.next_code += 1

                current_string = char
        
        if current_string:
            compressed_result.append(self.search(current_string))
            
        return compressed_result

    def decompress(self, compressed_codes):
        dictionary = {i: chr(i) for i in range(256)}
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
            dictionary[next_code] = previous_string + current_string[0]
            next_code += 1
            previous_code = current_code

        return result_text

# Test Bloğu
if __name__ == "__main__":
    lzw = LZWPatricia()
    # Patricia mantığını zorlamak için tekrar eden ama farklılaşan metin
    input_text = "banana_bandana_banana" 
    print(f"Original: {input_text}")
    
    compressed = lzw.compress(input_text)
    print(f"Compressed: {compressed}")
    
    decompressed = lzw.decompress(compressed)
    print(f"Decompressed: {decompressed}")
    
    if input_text == decompressed:
        print("SUCCESS: Patricia Trie LZW works!")  