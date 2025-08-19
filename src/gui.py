import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os
from .compressor import SequentialCompressor

class CompressionGUI:
    """Main GUI for the compression application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Parallel File Compressor - Module 1")
        self.root.geometry("700x500")
        
        # Initialize compressor
        self.compressor = SequentialCompressor()
        
        # Progress queue for thread communication
        self.progress_queue = queue.Queue()
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        
        # Operation state
        self.current_operation = None  # 'compress' or 'decompress'
        
        self.setup_ui()
        self.check_progress_queue()
    
    def setup_ui(self):
        """Create the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="File Compression Tool", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Input File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        input_entry = ttk.Entry(main_frame, textvariable=self.input_file, width=50)
        input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_input_file).grid(row=1, column=2, pady=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_file, width=50)
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_output_file).grid(row=2, column=2, pady=5)
        
        # Compression options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Chunk size selection
        ttk.Label(options_frame, text="Chunk Size:").grid(row=0, column=0, sticky=tk.W)
        self.chunk_size_var = tk.StringVar(value="1MB")
        chunk_combo = ttk.Combobox(options_frame, textvariable=self.chunk_size_var,
                                  values=["512KB", "1MB", "2MB", "4MB", "8MB"],
                                  state="readonly", width=10)
        chunk_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.compress_btn = ttk.Button(button_frame, text="Compress File", 
                                      command=self.start_compression)
        self.compress_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.decompress_btn = ttk.Button(button_frame, text="Decompress File", 
                                        command=self.start_decompression)
        self.decompress_btn.pack(side=tk.LEFT)
        
        # Quick decompress button (selects .pzip automatically)
        self.quick_decompress_btn = ttk.Button(button_frame, text="Quick Decompress", 
                                             command=self.quick_decompress)
        self.quick_decompress_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Add initial help message
        self.log_message("Welcome to File Compression Tool!")
        self.log_message("1. Select a file to compress OR select a .pzip file to decompress")
        self.log_message("2. Choose output location")
        self.log_message("3. Click appropriate button")
        self.log_message("-" * 50)
    
    def browse_input_file(self):
        """Open file dialog for input file selection."""
        filename = filedialog.askopenfilename(
            title="Select file to compress or .pzip file to decompress",
            filetypes=[
                ("All files", "*.*"),
                ("PZIP files", "*.pzip"),
                ("Text files", "*.txt"),
                ("Image files", "*.jpg;*.png;*.gif"),
                ("Document files", "*.pdf;*.doc;*.docx")
            ]
        )
        if filename:
            self.input_file.set(filename)
            self.auto_suggest_output_file(filename)
            self.log_message(f"Selected input file: {os.path.basename(filename)}")
    
    def auto_suggest_output_file(self, input_path):
        """Auto-suggest output filename based on input file."""
        base_name, ext = os.path.splitext(input_path)
        
        if ext.lower() == '.pzip':
            # Decompression: remove .pzip extension
            suggested_output = base_name
            self.log_message("Detected .pzip file - ready for decompression")
        else:
            # Compression: add .pzip extension
            suggested_output = f"{base_name}.pzip"
            self.log_message("Detected regular file - ready for compression")
        
        self.output_file.set(suggested_output)
    
    def browse_output_file(self):
        """Open file dialog for output file selection."""
        input_path = self.input_file.get().strip()
        
        if input_path.lower().endswith('.pzip'):
            # Decompression case
            base_name = os.path.splitext(input_path)[0]
            filename = filedialog.asksaveasfilename(
                title="Save decompressed file as",
                filetypes=[("All files", "*.*")],
                initialfile=os.path.basename(base_name)  # Fixed: was initialvalue
            )
        else:
            # Compression case
            if input_path:
                base_name = os.path.splitext(input_path)[0]
                default_name = f"{os.path.basename(base_name)}.pzip"
            else:
                default_name = "compressed.pzip"
            
            filename = filedialog.asksaveasfilename(
                title="Save compressed file as",
                defaultextension=".pzip",
                filetypes=[("PZIP files", "*.pzip"), ("All files", "*.*")],
                initialfile=default_name  # Fixed: was initialvalue
            )
        
        if filename:
            self.output_file.set(filename)
            self.log_message(f"Output will be saved as: {os.path.basename(filename)}")
    
    def get_chunk_size_bytes(self) -> int:
        """Convert chunk size string to bytes."""
        size_str = self.chunk_size_var.get()
        size_map = {
            "512KB": 512 * 1024,
            "1MB": 1024 * 1024,
            "2MB": 2 * 1024 * 1024,
            "4MB": 4 * 1024 * 1024,
            "8MB": 8 * 1024 * 1024
        }
        return size_map.get(size_str, 1024 * 1024)
    
    def log_message(self, message: str):
        """Add message to log area."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def progress_callback(self, message: str, percentage: float):
        """Callback for progress updates from compression thread."""
        self.progress_queue.put(('progress', message, percentage))
    
    def check_progress_queue(self):
        """Check for progress updates from background thread."""
        try:
            while True:
                item = self.progress_queue.get_nowait()
                if item[0] == 'progress':
                    _, message, percentage = item
                    self.status_var.set(message)
                    self.progress_var.set(percentage)
                    if not message.startswith("Error"):
                        self.log_message(message)
                elif item[0] == 'complete':
                    _, success, message = item
                    self.status_var.set(message)
                    self.progress_var.set(100 if success else 0)
                    self.log_message(message)
                    self.enable_buttons()
                    
                    if success:
                        messagebox.showinfo("Success", message)
                    else:
                        messagebox.showerror("Error", message)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_progress_queue)
    
    def disable_buttons(self):
        """Disable action buttons during operation."""
        self.compress_btn.config(state='disabled')
        self.decompress_btn.config(state='disabled')
        self.quick_decompress_btn.config(state='disabled')
    
    def enable_buttons(self):
        """Enable action buttons after operation."""
        self.compress_btn.config(state='normal')
        self.decompress_btn.config(state='normal')
        self.quick_decompress_btn.config(state='normal')
    
    def validate_files(self, input_path, output_path, operation):
        """Validate input and output files for the operation."""
        if not input_path or not output_path:
            return False, "Please select both input and output files."
        
        if not os.path.exists(input_path):
            return False, "Input file does not exist."
        
        if operation == 'compress':
            if input_path.lower().endswith('.pzip'):
                return False, "Cannot compress a .pzip file. Use decompress instead."
        elif operation == 'decompress':
            if not input_path.lower().endswith('.pzip'):
                return False, "Can only decompress .pzip files."
        
        # Check if input and output are the same
        if os.path.abspath(input_path) == os.path.abspath(output_path):
            return False, "Input and output files cannot be the same."
        
        return True, "Validation passed"
    
    def start_compression(self):
        """Start compression in background thread."""
        input_path = self.input_file.get().strip()
        output_path = self.output_file.get().strip()
        
        # Validate files
        valid, message = self.validate_files(input_path, output_path, 'compress')
        if not valid:
            messagebox.showerror("Validation Error", message)
            return
        
        # Update compressor chunk size
        chunk_size = self.get_chunk_size_bytes()
        self.compressor = SequentialCompressor(chunk_size)
        
        self.current_operation = 'compress'
        self.disable_buttons()
        self.progress_var.set(0)
        self.log_message(f"Starting compression of: {os.path.basename(input_path)}")
        self.log_message(f"Output: {os.path.basename(output_path)}")
        self.log_message(f"Chunk size: {self.chunk_size_var.get()}")
        
        # Start compression in background thread
        thread = threading.Thread(target=self._compression_worker, 
                                 args=(input_path, output_path))
        thread.daemon = True
        thread.start()
    
    def start_decompression(self):
        """Start decompression in background thread."""
        input_path = self.input_file.get().strip()
        output_path = self.output_file.get().strip()
        
        # Validate files
        valid, message = self.validate_files(input_path, output_path, 'decompress')
        if not valid:
            messagebox.showerror("Validation Error", message)
            return
        
        self.current_operation = 'decompress'
        self.disable_buttons()
        self.progress_var.set(0)
        self.log_message(f"Starting decompression of: {os.path.basename(input_path)}")
        self.log_message(f"Output: {os.path.basename(output_path)}")
        
        # Start decompression in background thread
        thread = threading.Thread(target=self._decompression_worker, 
                                 args=(input_path, output_path))
        thread.daemon = True
        thread.start()
    
    def quick_decompress(self):
        """Quick decompress - automatically select .pzip file and output location."""
        pzip_file = filedialog.askopenfilename(
            title="Select .pzip file to decompress",
            filetypes=[("PZIP files", "*.pzip"), ("All files", "*.*")]
        )
        
        if not pzip_file:
            return
        
        # Auto-suggest output filename (remove .pzip extension)
        base_name = os.path.splitext(pzip_file)[0]
        output_file = filedialog.asksaveasfilename(
            title="Save decompressed file as",
            initialfile=os.path.basename(base_name),  # Fixed: was initialvalue
            filetypes=[("All files", "*.*")]
        )
        
        if not output_file:
            return
        
        # Set the fields and start decompression
        self.input_file.set(pzip_file)
        self.output_file.set(output_file)
        
        self.log_message(f"Quick decompress: {os.path.basename(pzip_file)} → {os.path.basename(output_file)}")
        
        self.current_operation = 'decompress'
        self.disable_buttons()
        self.progress_var.set(0)
        
        # Start decompression in background thread
        thread = threading.Thread(target=self._decompression_worker, 
                                 args=(pzip_file, output_file))
        thread.daemon = True
        thread.start()
    
    def _compression_worker(self, input_path: str, output_path: str):
        """Background worker for compression."""
        try:
            success = self.compressor.compress_file(input_path, output_path, 
                                                   self.progress_callback)
            if success:
                original_size = os.path.getsize(input_path)
                compressed_size = os.path.getsize(output_path)
                ratio = (1 - compressed_size / original_size) * 100
                message = f"Compression completed! Original: {original_size:,} bytes, Compressed: {compressed_size:,} bytes. Saved {ratio:.1f}% space."
            else:
                message = "Compression failed. Check the log for details."
            
            self.progress_queue.put(('complete', success, message))
            
        except Exception as e:
            self.progress_queue.put(('complete', False, f"Compression error: {str(e)}"))
    
    def _decompression_worker(self, input_path: str, output_path: str):
        """Background worker for decompression."""
        try:
            success = self.compressor.decompress_file(input_path, output_path, 
                                                     self.progress_callback)
            if success:
                decompressed_size = os.path.getsize(output_path)
                message = f"Decompression completed! Output size: {decompressed_size:,} bytes."
            else:
                message = "Decompression failed. Check the log for details."
            
            self.progress_queue.put(('complete', success, message))
            
        except Exception as e:
            self.progress_queue.put(('complete', False, f"Decompression error: {str(e)}"))

def create_gui():
    """Create and return the main GUI window."""
    root = tk.Tk()
    app = CompressionGUI(root)
    return root, app