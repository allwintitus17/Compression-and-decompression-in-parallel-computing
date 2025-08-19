import zlib
import struct
import os
from typing import Callable, Optional, Tuple
from .utils import FileChunker

class SequentialCompressor:
    """Sequential file compression using zlib."""
    
    def __init__(self, chunk_size: int = 1024 * 1024):
        self.chunker = FileChunker(chunk_size)
        self.compression_level = 6  # Default zlib compression level
    
    def compress_file(self, input_path: str, output_path: str, 
                     progress_callback: Optional[Callable] = None) -> bool:
        """
        Compress file sequentially.
        
        Args:
            input_path: Path to input file
            output_path: Path to output .pzip file
            progress_callback: Function to call with progress updates
        
        Returns:
            True if successful, False otherwise
        """
        try:
            file_size, total_chunks = self.chunker.get_file_info(input_path)
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_path, 'wb') as output_file:
                # Write file header
                self._write_header(output_file, file_size, total_chunks)
                
                # Compress chunks sequentially
                chunk_count = 0
                for chunk in self.chunker.read_chunks(input_path):
                    compressed_chunk = zlib.compress(chunk, self.compression_level)
                    
                    # Write chunk size and compressed data
                    self._write_chunk(output_file, compressed_chunk)
                    
                    chunk_count += 1
                    if progress_callback:
                        progress = (chunk_count / total_chunks) * 100
                        progress_callback(f"Compressing chunk {chunk_count}/{total_chunks}", progress)
            
            if progress_callback:
                progress_callback("Compression completed successfully!", 100)
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"Compression error: {str(e)}", 0)
            return False
    
    def decompress_file(self, input_path: str, output_path: str,
                       progress_callback: Optional[Callable] = None) -> bool:
        """
        Decompress .pzip file.
        
        Args:
            input_path: Path to .pzip file
            output_path: Path to output file
            progress_callback: Function to call with progress updates
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(input_path):
                if progress_callback:
                    progress_callback("Error: Input file does not exist", 0)
                return False
            
            # Check minimum file size
            file_size = os.path.getsize(input_path)
            if file_size < 24:  # Minimum header size
                if progress_callback:
                    progress_callback(f"Error: File too small ({file_size} bytes). Not a valid .pzip file", 0)
                return False
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(input_path, 'rb') as input_file:
                # Read and validate header
                try:
                    original_size, total_chunks = self._read_header(input_file)
                    if progress_callback:
                        progress_callback(f"Starting decompression: {total_chunks} chunks", 0)
                except ValueError as e:
                    if progress_callback:
                        progress_callback(f"Invalid .pzip file: {str(e)}", 0)
                    return False
                
                with open(output_path, 'wb') as output_file:
                    chunk_count = 0
                    
                    for chunk_num in range(total_chunks):
                        # Read chunk
                        try:
                            compressed_chunk = self._read_chunk(input_file)
                            if compressed_chunk is None:
                                if progress_callback:
                                    progress_callback(f"Error: Unexpected end of file at chunk {chunk_num + 1}", 0)
                                return False
                            
                            # Decompress and write
                            decompressed_chunk = zlib.decompress(compressed_chunk)
                            output_file.write(decompressed_chunk)
                            
                            chunk_count += 1
                            if progress_callback:
                                progress = (chunk_count / total_chunks) * 100
                                progress_callback(f"Decompressing chunk {chunk_count}/{total_chunks}", progress)
                                
                        except (zlib.error, struct.error) as e:
                            if progress_callback:
                                progress_callback(f"Error decompressing chunk {chunk_num + 1}: {str(e)}", 0)
                            return False
            
            # Verify output file size matches expected
            actual_size = os.path.getsize(output_path)
            if actual_size != original_size:
                if progress_callback:
                    progress_callback(f"Size mismatch: expected {original_size}, got {actual_size}", 0)
                return False
            
            if progress_callback:
                progress_callback("Decompression completed successfully!", 100)
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"Decompression error: {str(e)}", 0)
            return False
    
    def _write_header(self, file, original_size: int, total_chunks: int):
        """Write file header with metadata."""
        # Magic bytes: 'PZIP'
        file.write(b'PZIP')
        # Version: 1
        file.write(struct.pack('<I', 1))
        # Original file size
        file.write(struct.pack('<Q', original_size))
        # Total chunks
        file.write(struct.pack('<I', total_chunks))
        # Chunk size
        file.write(struct.pack('<I', self.chunker.chunk_size))
    
    def _write_chunk(self, file, compressed_data: bytes):
        """Write compressed chunk with size prefix."""
        chunk_size = len(compressed_data)
        file.write(struct.pack('<I', chunk_size))
        file.write(compressed_data)
    
    def _read_header(self, file) -> Tuple[int, int]:
        """Read file header and return (original_size, total_chunks)."""
        magic = file.read(4)
        if magic != b'PZIP':
            raise ValueError(f"Invalid magic bytes. Expected b'PZIP', got {magic}")
        
        version = struct.unpack('<I', file.read(4))[0]
        if version != 1:
            raise ValueError(f"Unsupported version: {version}")
        
        original_size = struct.unpack('<Q', file.read(8))[0]
        total_chunks = struct.unpack('<I', file.read(4))[0]
        chunk_size = struct.unpack('<I', file.read(4))[0]
        
        # Update chunker chunk size to match file
        self.chunker.chunk_size = chunk_size
        
        return original_size, total_chunks
    
    def _read_chunk(self, file) -> Optional[bytes]:
        """Read compressed chunk."""
        size_data = file.read(4)
        if len(size_data) < 4:
            return None
        
        chunk_size = struct.unpack('<I', size_data)[0]
        if chunk_size == 0:
            return None
        
        chunk_data = file.read(chunk_size)
        if len(chunk_data) != chunk_size:
            raise ValueError(f"Expected {chunk_size} bytes, got {len(chunk_data)}")
        
        return chunk_data