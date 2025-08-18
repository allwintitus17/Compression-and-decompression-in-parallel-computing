#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compressor import SequentialCompressor
import time

def test_compression():
    """Basic compression test."""
    compressor = SequentialCompressor(chunk_size=1024*1024)  # 1MB chunks
    
    test_file = "tests/test_files/medium_test.txt"
    output_file = "output/test_compressed.pzip"
    decompressed_file = "output/test_decompressed.txt"
    
    if not os.path.exists(test_file):
        print("Test file not found. Please create test files first.")
        return
    
    print(f"Testing compression of: {test_file}")
    
    # Test compression
    start_time = time.time()
    success = compressor.compress_file(test_file, output_file)
    compression_time = time.time() - start_time
    
    if success:
        original_size = os.path.getsize(test_file)
        compressed_size = os.path.getsize(output_file)
        ratio = (1 - compressed_size / original_size) * 100
        
        print(f"✓ Compression successful in {compression_time:.2f}s")
        print(f"  Original size: {original_size:,} bytes")
        print(f"  Compressed size: {compressed_size:,} bytes")
        print(f"  Compression ratio: {ratio:.1f}%")
        
        # Test decompression
        start_time = time.time()
        success = compressor.decompress_file(output_file, decompressed_file)
        decompression_time = time.time() - start_time
        
        if success:
            print(f"✓ Decompression successful in {decompression_time:.2f}s")
            
            # Verify integrity
            with open(test_file, 'rb') as f1, open(decompressed_file, 'rb') as f2:
                if f1.read() == f2.read():
                    print("✓ File integrity verified - files match perfectly!")
                else:
                    print("✗ File integrity check failed!")
        else:
            print("✗ Decompression failed")
    else:
        print("✗ Compression failed")

if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    test_compression()