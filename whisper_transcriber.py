import whisper
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import queue
from pathlib import Path

class WhisperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Audio Transcription")
        self.root.geometry("600x400")
        
        # Variables
        self.selected_files = []
        self.model = None
        self.current_model_size = "base"
        
        # Initialize queue and threading components
        self.transcription_queue = queue.Queue()
        self.is_processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="Whisper Audio Transcription", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # File selection frame
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Button(file_frame, text="Select Audio Files", 
                 command=self.select_files, bg="#4CAF50", fg="white",
                 font=("Arial", 10, "bold")).pack(side="left")
        
        tk.Button(file_frame, text="Select Folder", 
                 command=self.select_folder, bg="#2196F3", fg="white",
                 font=("Arial", 10, "bold")).pack(side="left", padx=(10, 0))
        
        # Selected files display
        self.files_listbox = tk.Listbox(self.root, height=8)
        self.files_listbox.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Settings frame
        settings_frame = tk.Frame(self.root)
        settings_frame.pack(pady=10, padx=20, fill="x")
        
        # Model selection
        tk.Label(settings_frame, text="Model Size:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(settings_frame, textvariable=self.model_var, 
                                  values=["tiny", "base", "small", "medium", "large"])
        model_combo.grid(row=0, column=1, padx=(10, 20), sticky="w")
        
        # Language selection
        tk.Label(settings_frame, text="Language:", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="w")
        self.language_var = tk.StringVar(value="auto")
        language_combo = ttk.Combobox(settings_frame, textvariable=self.language_var,
                                     values=["auto", "english", "spanish", "french", "german", "italian", "portuguese", "chinese", "japanese", "korean"])
        language_combo.grid(row=0, column=3, padx=(10, 0), sticky="w")
        
        # Output format
        tk.Label(settings_frame, text="Output Format:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.format_var = tk.StringVar(value="txt")
        format_combo = ttk.Combobox(settings_frame, textvariable=self.format_var,
                                   values=["txt", "srt", "vtt", "json", "all"])
        format_combo.grid(row=1, column=1, padx=(10, 0), sticky="w", pady=(10, 0))
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready to transcribe")
        tk.Label(self.root, textvariable=self.progress_var, font=("Arial", 10)).pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress_bar.pack(pady=5, padx=20, fill="x")
        
        # Transcribe button
        self.transcribe_btn = tk.Button(self.root, text="Start Transcription", 
                                       command=self.start_transcription, 
                                       bg="#FF9800", fg="white", font=("Arial", 12, "bold"))
        self.transcribe_btn.pack(pady=10)
        
        # Pre-download model button
        self.download_btn = tk.Button(self.root, text="Pre-download Model", 
                                     command=self.download_model, 
                                     bg="#9C27B0", fg="white", font=("Arial", 10))
        self.download_btn.pack(pady=5)
        
    def download_model(self):
        """Pre-download the selected model"""
        if self.is_processing:
            messagebox.showwarning("Warning", "Cannot download model while transcription is in progress!")
            return
            
        model_size = self.model_var.get()
        
        # Disable buttons
        self.download_btn.config(state="disabled")
        self.transcribe_btn.config(state="disabled")
        self.progress_bar.start()
        
        def download_worker():
            try:
                self.progress_var.set(f"Downloading {model_size} model...")
                self.model = whisper.load_model(model_size)
                self.current_model_size = model_size
                self.progress_var.set(f"Model {model_size} downloaded successfully!")
                messagebox.showinfo("Success", f"Model '{model_size}' has been downloaded and cached successfully!")
                
            except Exception as e:
                error_msg = str(e)
                self.progress_var.set("Model download failed")
                if "urlopen error" in error_msg or "connection" in error_msg.lower():
                    messagebox.showerror("Download Failed", 
                        f"Failed to download model due to network issues.\n\n"
                        f"Troubleshooting steps:\n"
                        f"1. Check your internet connection\n"
                        f"2. Disable firewall/antivirus temporarily\n"
                        f"3. Try using a VPN if in a restricted network\n"
                        f"4. Contact your network administrator\n\n"
                        f"Error: {error_msg}")
                else:
                    messagebox.showerror("Error", f"Failed to download model: {error_msg}")
            
            finally:
                # Re-enable buttons
                self.download_btn.config(state="normal")
                self.transcribe_btn.config(state="normal")
                self.progress_bar.stop()
        
        # Start download in separate thread
        thread = threading.Thread(target=download_worker)
        thread.daemon = True
        thread.start()
        
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.m4a *.flac *.aac *.ogg *.wma"),
                ("All Files", "*.*")
            ]
        )
        self.selected_files = list(files)
        self.update_file_list()
        
    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Audio Files")
        if folder:
            audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma'}
            files = []
            for file_path in Path(folder).rglob('*'):
                if file_path.suffix.lower() in audio_extensions:
                    files.append(str(file_path))
            self.selected_files = files
            self.update_file_list()
            
    def update_file_list(self):
        self.files_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.files_listbox.insert(tk.END, os.path.basename(file))
            
    def load_model(self, model_size):
        if self.model is None or self.current_model_size != model_size:
            self.progress_var.set(f"Loading {model_size} model...")
            self.root.update()
            
            try:
                # Try to load the model with error handling
                self.model = whisper.load_model(model_size)
                self.current_model_size = model_size
                
            except Exception as e:
                error_msg = str(e)
                if "urlopen error" in error_msg or "connection" in error_msg.lower():
                    # Network connection issue
                    messagebox.showerror("Connection Error", 
                        f"Failed to download Whisper model due to network issues.\n\n"
                        f"Solutions:\n"
                        f"1. Check your internet connection\n"
                        f"2. Try again later\n"
                        f"3. If behind a firewall/proxy, configure network settings\n"
                        f"4. Pre-download models manually\n\n"
                        f"Error: {error_msg}")
                else:
                    messagebox.showerror("Model Loading Error", f"Failed to load model: {error_msg}")
                
                self.progress_var.set("Model loading failed")
                raise e
            
    def transcribe_file(self, file_path, language, output_format):
        try:
            # Transcribe
            if language == "auto":
                result = self.model.transcribe(file_path)
            else:
                result = self.model.transcribe(file_path, language=language)
            
            # Save output
            base_name = os.path.splitext(file_path)[0]
            
            if output_format == "all":
                formats = ["txt", "srt", "vtt", "json"]
            else:
                formats = [output_format]
                
            for fmt in formats:
                output_path = f"{base_name}.{fmt}"
                
                if fmt == "txt":
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result["text"])
                        
                elif fmt == "srt":
                    self.write_srt(result, output_path)
                    
                elif fmt == "vtt":
                    self.write_vtt(result, output_path)
                    
                elif fmt == "json":
                    import json
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                        
            return True, None
            
        except Exception as e:
            return False, str(e)
            
    def write_srt(self, result, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result["segments"]):
                start_time = self.format_time_srt(segment["start"])
                end_time = self.format_time_srt(segment["end"])
                f.write(f"{i + 1}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
                
    def write_vtt(self, result, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in result["segments"]:
                start_time = self.format_time_vtt(segment["start"])
                end_time = self.format_time_vtt(segment["end"])
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
                
    def format_time_srt(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
    def format_time_vtt(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
        
    def start_transcription(self):
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select audio files first!")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Transcription is already in progress!")
            return
            
        # Disable button and start progress
        self.transcribe_btn.config(state="disabled")
        self.progress_bar.start()
        self.is_processing = True
        
        # Start transcription in separate thread
        thread = threading.Thread(target=self.transcription_worker)
        thread.daemon = True
        thread.start()
        
    def transcription_worker(self):
        """Worker thread for handling transcription tasks"""
        # Initialize counters at the beginning of the method
        successful = 0
        failed = 0
        
        try:
            # Load model with retry logic
            model_size = self.model_var.get()
            
            # Try loading model with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.load_model(model_size)
                    break  # Success, exit retry loop
                except Exception as e:
                    if attempt < max_retries - 1:  # Not the last attempt
                        self.progress_var.set(f"Model loading failed, retrying... ({attempt + 1}/{max_retries})")
                        import time
                        time.sleep(2)  # Wait 2 seconds before retry
                    else:
                        # Last attempt failed
                        self.progress_var.set("Model loading failed - check internet connection")
                        return  # Exit the worker
            
            # Get settings
            language = self.language_var.get()
            output_format = self.format_var.get()
            
            # Process each file
            total_files = len(self.selected_files)
            
            for i, file_path in enumerate(self.selected_files):
                try:
                    # Update progress
                    filename = os.path.basename(file_path)
                    self.progress_var.set(f"Processing {i+1}/{total_files}: {filename}")
                    
                    # Transcribe file
                    success, error = self.transcribe_file(file_path, language, output_format)
                    
                    if success:
                        successful += 1
                    else:
                        failed += 1
                        print(f"Error transcribing {file_path}: {error}")
                        
                except Exception as e:
                    print(f"Error transcribing {file_path}: {str(e)}")
                    failed += 1
        
        except Exception as e:
            print(f"Worker thread error: {str(e)}")
        
        finally:
            # Update final progress and reset UI
            if successful > 0 or failed > 0:
                self.progress_var.set(f"Completed! {successful} successful, {failed} failed")
            else:
                self.progress_var.set("Transcription cancelled due to model loading failure")
            self.progress_bar.stop()
            self.transcribe_btn.config(state="normal")
            self.is_processing = False

# Simple command-line version
def transcribe_simple(file_path, model_size="base", language="auto", output_format="txt"):
    """
    Simple function to transcribe a single file
    """
    print(f"Loading {model_size} model...")
    model = whisper.load_model(model_size)
    
    print(f"Transcribing {file_path}...")
    if language == "auto":
        result = model.transcribe(file_path)
    else:
        result = model.transcribe(file_path, language=language)
    
    # Save transcript
    base_name = os.path.splitext(file_path)[0]
    output_path = f"{base_name}.{output_format}"
    
    if output_format == "txt":
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
    
    print(f"Transcript saved to: {output_path}")
    return result["text"]

# Batch processing function
def transcribe_batch(folder_path, model_size="base", language="auto", output_format="txt"):
    """
    Transcribe all audio files in a folder
    """
    audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma'}
    audio_files = []
    
    for file_path in Path(folder_path).rglob('*'):
        if file_path.suffix.lower() in audio_extensions:
            audio_files.append(str(file_path))
    
    if not audio_files:
        print("No audio files found in the specified folder.")
        return
    
    print(f"Found {len(audio_files)} audio files")
    print(f"Loading {model_size} model...")
    model = whisper.load_model(model_size)
    
    for i, file_path in enumerate(audio_files):
        print(f"Transcribing {os.path.basename(file_path)} ({i+1}/{len(audio_files)})")
        
        try:
            if language == "auto":
                result = model.transcribe(file_path)
            else:
                result = model.transcribe(file_path, language=language)
            
            base_name = os.path.splitext(file_path)[0]
            output_path = f"{base_name}.{output_format}"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result["text"])
                
            print(f"✓ Saved: {output_path}")
            
        except Exception as e:
            print(f"✗ Error transcribing {file_path}: {e}")
    
    print("Batch transcription completed!")

if __name__ == "__main__":
    # Uncomment one of these options:
    
    # Option 1: GUI Version (recommended for most users)
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()
    
    # Option 2: Simple single file transcription
    # transcribe_simple("path/to/your/audio.mp3", model_size="base", language="english")
    
    # Option 3: Batch process entire folder
    # transcribe_batch("path/to/folder/with/audio/files", model_size="base", language="english")