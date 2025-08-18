import zlib
import struct
import os
from typing import Callable, Optional, Tuple
from utils import FileChunker  # assumes utils.py is in the same folder

class SequentialCompressor:
    """Sequential file compression using zlib."""

    def __init__(self, chunk_size: int = 1024 * 1024):
        self.chunker = FileChunker(chunk_size)
        self.compression_level = 6  # Default zlib compression level

    def compress_file(
        self,
        input_path: str,
        output_path: str,
        progress_callback: Optional[Callable] = None
    ) -> bool:
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

            with open(output_path, 'wb') as output_file:
                self._write_header(output_file, file_size, total_chunks)

                chunk_count = 0
                for chunk in self.chunker.read_chunks(input_path):
                    compressed_chunk = zlib.compress(chunk, self.compression_level)
                    self._write_chunk(output_file, compressed_chunk)

                    chunk_count += 1
                    if progress_callback:
                        progress = (chunk_count / total_chunks) * 100
                        progress_callback(
                            f"Compressing chunk {chunk_count}/{total_chunks}", progress
                        )

            return True

        except Exception as e:
            if progress_callback:
                progress_callback(f"Error: {str(e)}", 0)
            return False

    def decompress_file(
        self,
        input_path: str,
        output_path: str,
        progress_callback: Optional[Callable] = None
    ) -> bool:
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
            with open(input_path, 'rb') as input_file:
                original_size, total_chunks = self._read_header(input_file)

                with open(output_path, 'wb') as output_file:
                    chunk_count = 0

                    for _ in range(total_chunks):
                        compressed_chunk = self._read_chunk(input_file)
                        if compressed_chunk is None:
                            break

                        decompressed_chunk = zlib.decompress(compressed_chunk)
                        output_file.write(decompressed_chunk)

                        chunk_count += 1
                        if progress_callback:
                            progress = (chunk_count / total_chunks) * 100
                            progress_callback(
                                f"Decompressing chunk {chunk_count}/{total_chunks}", progress
                            )

            return True

        except Exception as e:
            if progress_callback:
                progress_callback(f"Error: {str(e)}", 0)
            return False

    def _write_header(self, file, original_size: int, total_chunks: int):
        """Write file header with metadata."""
        file.write(b'PZIP')  # Magic bytes
        file.write(struct.pack('<I', 1))  # Version
        file.write(struct.pack('<Q', original_size))
        file.write(struct.pack('<I', total_chunks))
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
            raise ValueError("Invalid file format")

        version = struct.unpack('<I', file.read(4))[0]
        original_size = struct.unpack('<Q', file.read(8))[0]
        total_chunks = struct.unpack('<I', file.read(4))[0]
        chunk_size = struct.unpack('<I', file.read(4))[0]

        return original_size, total_chunks

    def _read_chunk(self, file) -> Optional[bytes]:
        """Read compressed chunk."""
        size_data = file.read(4)
        if len(size_data) < 4:
            return None

        chunk_size = struct.unpack('<I', size_data)[0]
        return file.read(chunk_size)
