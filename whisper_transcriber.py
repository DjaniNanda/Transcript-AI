import whisper
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
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
        self.transcribe_btn.pack(pady=20)
        
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
            self.model = whisper.load_model(model_size)
            self.current_model_size = model_size
            
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
            
        # Disable button and start progress
        self.transcribe_btn.config(state="disabled")
        self.progress_bar.start()
        
        # Start transcription in separate thread
        thread = threading.Thread(target=self.transcription_worker)
        thread.daemon = True
        thread.start()
        
    def transcription_worker(self):
        model_size = self.model_var.get()
        language = self.language_var.get()
        output_format = self.format_var.get()
        
        try:
            # Load model
            self.load_model(model_size)
            
            successful = 0
            failed = 0
            
            for i, file_path in enumerate(self.selected_files):
                filename = os.path.basename(file_path)
                self.progress_var.set(f"Transcribing {filename} ({i+1}/{len(self.selected_files)})")
                self.root.update()
                
                success, error = self.transcribe_file(file_path, language, output_format)
                
                if success:
                    successful += 1
                else:
                    failed += 1
                    print(f"Error transcribing {filename}: {error}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
        finally:
            # Re-enable button and stop progress
            self.progress_bar.stop()
            self.transcribe_btn.config(state="normal")
            self.progress_var.set(f"Completed! {successful} successful, {failed} failed")
            
            if successful > 0:
                messagebox.showinfo("Complete", 
                    f"Transcription completed!\n{successful} files processed successfully.\n"
                    f"Transcripts saved in the same folder as your audio files.")

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