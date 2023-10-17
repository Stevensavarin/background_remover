import os
from datetime import datetime
from rembg import remove
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tqdm import tqdm
import threading

class BackgroundRemover:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder

    def process_images(self, input_images, progress_bar, completion_label):
        today = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        processed_folder = os.path.join(self.output_folder, today)
        os.makedirs(processed_folder, exist_ok=True)

        for input_path in input_images:
            filename = os.path.basename(input_path)
            output_path = os.path.join(processed_folder, filename)
            self._remove_background(input_path, output_path)
            self._move_originals(input_path, processed_folder)
            progress_bar.step(1)

        completion_label.config(text="Image processing completed!")

    def _remove_background(self, input_p, output_p):
        with open(input_p, "rb") as inp, open(output_p, "wb") as outp:
            background_output = remove(inp.read())
            outp.write(background_output)

    def _move_originals(self, input_p, dest_p):
        originals_folder = os.path.join(dest_p, "originals")
        os.makedirs(originals_folder, exist_ok=True)

        filename = os.path.basename(input_p)
        new_path = os.path.join(originals_folder, filename)
        os.rename(input_p, new_path)

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Remover by Steven")
        self.input_images = []
        
        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10)

        self.image_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE)
        self.image_listbox.pack(side=tk.LEFT)

        listbox_scroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        listbox_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=listbox_scroll.set)
  
        add_button = tk.Button(frame, text="Add Images", command=self.add_images)
        add_button.pack(side=tk.LEFT)

        remove_button = tk.Button(frame, text="Remove Selected", command=self.remove_images)
        remove_button.pack(side=tk.LEFT)

        process_button = tk.Button(frame, text="Process Images", command=self.process_images)
        process_button.pack(side=tk.LEFT)

        exit_button = tk.Button(frame, text="Exit", command=root.quit)
        exit_button.pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.completion_label = tk.Label(self.root, text="")
        self.completion_label.pack(pady=10)

    def add_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_paths:
            for file_path in file_paths:
                self.input_images.append(file_path)
                self.image_listbox.insert(tk.END, os.path.basename(file_path))

    def remove_images(self):
        selected_indices = self.image_listbox.curselection()
        for idx in reversed(selected_indices):
            self.input_images.pop(idx)
            self.image_listbox.delete(idx)

    def process_images(self):
        if self.input_images:
            self.progress_bar["maximum"] = len(self.input_images)
            self.progress_bar["value"] = 0
            self.completion_label.config(text="")

            remover = BackgroundRemover("input", "output")
            process_thread = threading.Thread(target=self.process_images_thread, args=(remover,))
            process_thread.start()

    def process_images_thread(self, remover):
        remover.process_images(self.input_images, self.progress_bar, self.completion_label)
        self.input_images.clear()
        self.image_listbox.delete(0, tk.END)

if __name__ == "__main__":
    window = tk.Tk()
    app = BackgroundRemoverApp(window)
    window.mainloop()

