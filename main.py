import time
import os
import csv
import tracemalloc

from src.lzw import LZW
from src.lzw_trie import LZWTrie
from src.lzw_patricia import LZWPatricia

def save_output_file(filename, data):
    with open(filename, 'w', encoding='latin-1') as f:
        if isinstance(data, list): 
            f.write(",".join(map(str, data)))
        else:
            f.write(data)

def save_dictionary_csv(compressor, method_name, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Code", "String"])

        # Case 1: Standard Dictionary (Task 1)
        if hasattr(compressor, 'dictionary') and isinstance(compressor.dictionary, dict):
            sorted_items = sorted(compressor.dictionary.items(), key=lambda item: item[1])
            for k, v in sorted_items:
                writer.writerow([v, k])

        # Case 2: Tree Based (Trie / Patricia)
        elif hasattr(compressor, 'root'):
            all_codes = []
            
            def traverse(node, current_str):
                if node.code != -1:
                    all_codes.append((node.code, current_str))
                
                for char, child in node.children.items():
                    # Handle Patricia labels vs Trie chars
                    segment = child.label if hasattr(child, 'label') else char
                    traverse(child, current_str + segment)

            traverse(compressor.root, "")
            
            all_codes.sort(key=lambda x: x[0])
            for code, string in all_codes:
                writer.writerow([code, string])

def run_experiment(input_file, CompressorClass, method_name):
    print(f"\n--- Testing Method: {method_name} ---")
    
    try:
        with open(input_file, 'r', encoding='latin-1') as f:
            uncompressed_data = f.read()
    except FileNotFoundError:
        print("File not found.")
        return

    original_size = len(uncompressed_data)
    
    # Measure Compression
    tracemalloc.start()
    start_time = time.time()
    
    compressor = CompressorClass()
    compressed_data = compressor.compress(uncompressed_data)
    
    end_time = time.time()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    comp_time = end_time - start_time
    peak_mem_mb = peak_mem / (1024 * 1024)
    compressed_size = len(compressed_data) * 2 

    # Measure Decompression
    start_time_dec = time.time()
    decompressed_data = compressor.decompress(compressed_data)
    end_time_dec = time.time()
    dec_time = end_time_dec - start_time_dec

    is_valid = (uncompressed_data == decompressed_data)
    status = "SUCCESS" if is_valid else "FAIL"

    ratio = original_size / compressed_size if compressed_size > 0 else 0
    throughput = (original_size / (1024*1024)) / comp_time if comp_time > 0 else 0

    print(f"Status: {status}")
    print(f"Time (Comp): {comp_time:.4f} s")
    print(f"Time (Decomp): {dec_time:.4f} s")
    print(f"Throughput: {throughput:.2f} MB/s")
    print(f"Peak Memory: {peak_mem_mb:.4f} MB")
    print(f"Ratio: {ratio:.2f}")

    # Save outputs
    os.makedirs("output", exist_ok=True)
    base_name = os.path.basename(input_file)
    save_output_file(f"output/{method_name}_{base_name}.lzw", compressed_data)
    save_output_file(f"output/{method_name}_{base_name}_decoded.txt", decompressed_data)
    save_dictionary_csv(compressor, method_name, f"output/{method_name}_dictionary.csv")

def main():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    test_file = "data/sample.txt"
    with open(test_file, 'w', encoding='latin-1') as f:
        f.write("TOBEORNOTTOBEORTOBEORNOT" * 500) 

    files = [test_file] 

    for filepath in files:
        run_experiment(filepath, LZW, "Baseline_Array")
        run_experiment(filepath, LZWTrie, "Trie_Based")
        run_experiment(filepath, LZWPatricia, "Patricia_Trie")

if __name__ == "__main__":
    main()