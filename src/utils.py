import os
import zlib
from typing import Iterator, Tuple

class FileChunker:
    """Handles reading large files in manageable chunks."""
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # Default 1MB chunks
        self.chunk_size = chunk_size
    
    def read_chunks(self, file_path: str) -> Iterator[bytes]:
        """Generator that yields file chunks."""
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
    
    def get_file_info(self, file_path: str) -> Tuple[int, int]:
        """Returns (file_size, estimated_chunks)."""
        file_size = os.path.getsize(file_path)
        estimated_chunks = (file_size + self.chunk_size - 1) // self.chunk_size
        return file_size, estimated_chunks