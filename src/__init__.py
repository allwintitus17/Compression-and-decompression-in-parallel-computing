"""
Parallel File Compressor Package
Module 1: Sequential Compression with GUI
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .compressor import SequentialCompressor
from .utils import FileChunker
from .gui import CompressionGUI, create_gui

__all__ = ['SequentialCompressor', 'FileChunker', 'CompressionGUI', 'create_gui']