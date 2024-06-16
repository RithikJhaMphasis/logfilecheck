import tkinter as tk
from tkinter import filedialog, messagebox
from bs4 import BeautifulSoup
import re
import json
import os

# Load master file
master_file = 'master.json'
if not os.path.exists(master_file):
    master_data = {
        "404": "Page not found",
        "500": "Internal Server Error",
        "503": "Database Connection Failed"
    }
    with open(master_file, 'w') as f:
        json.dump(master_data, f)
else:
    with open(master_file) as f:
        master_data = json.load(f)

# Function to extract error codes from log files
def extract_errors_from_log(log_file):
    error_pattern = re.compile(r'Error:.*?Code (\d+)')
    errors = []

    if log_file.endswith('.html'):
        with open(log_file, 'r') as f:
            soup = BeautifulSoup(f, 'html.parser')
            for p in soup.find_all('p'):
                match = error_pattern.search(p.text)
                if match:
                    errors.append(match.group(1))
    elif log_file.endswith('.txt'):
        with open(log_file, 'r') as f:
            for line in f:
                match = error_pattern.search(line)
                if match:
                    errors.append(match.group(1))
    
    return errors

# Function to summarize errors based on master file
def summarize_errors(errors, master_data):
    summary = {}
    for code in errors:
        if code in master_data:
            error_type = master_data[code]
            if error_type in summary:
                summary[error_type] += 1
            else:
                summary[error_type] = 1
    return summary

# Function to process selected files
def process_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Log files", "*.html *.txt")])
    if not file_paths:
        return
    
    all_errors = []
    for file_path in file_paths:
        all_errors.extend(extract_errors_from_log(file_path))
    
    error_summary = summarize_errors(all_errors, master_data)

    summary_text.delete(1.0, tk.END)
    summary_text.insert(tk.END, "Error Summary:\n")
    for error_type, count in error_summary.items():
        summary_text.insert(tk.END, f"{error_type}: {count}\n")

# Function to save summary to a text file
def save_summary():
    summary_content = summary_text.get(1.0, tk.END).strip()
    if not summary_content:
        messagebox.showwarning("Warning", "No summary to save.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if save_path:
        with open(save_path, 'w') as f:
            f.write(summary_content)
        messagebox.showinfo("Success", "Summary saved successfully.")

# Setting up the GUI
root = tk.Tk()
root.title("Log File Error Summarizer")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

select_button = tk.Button(frame, text="Select Log Files", command=process_files)
select_button.pack(pady=5)

summary_text = tk.Text(frame, width=50, height=15)
summary_text.pack(pady=5)

save_button = tk.Button(frame, text="Save Summary to File", command=save_summary)
save_button.pack(pady=5)

root.mainloop()
