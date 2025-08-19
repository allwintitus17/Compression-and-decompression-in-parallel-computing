#!/usr/bin/env python3
"""
Parallel File Compressor - Module 1
Sequential compression with GUI interface.
"""

import sys
import os
import tkinter as tk

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui import create_gui

def main():
    """Main application entry point."""
    try:
        # Create GUI
        root, app = create_gui()
        
        # Center window on screen
        root.update_idletasks()
        width = 700
        height = 500
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make window resizable
        root.minsize(600, 400)
        
        print("="*60)
        print("🚀 Starting Parallel File Compressor GUI...")
        print("="*60)
        print("📁 Project directory:", os.path.dirname(os.path.abspath(__file__)))
        print("🔧 Python version:", sys.version.split()[0])
        print("💻 Platform:", sys.platform)
        print("="*60)
        print("✅ GUI loaded successfully!")
        print("📝 Check the application window for instructions.")
        print("="*60)
        
        # Start the GUI event loop
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user.")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Try running: python tests/test_basic.py first")
        sys.exit(1)

if __name__ == "__main__":
    main()