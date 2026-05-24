import customtkinter as ctk
import tkinter as tk
import os, base64, traceback
from tkinterdnd2 import TkinterDnD, DND_FILES
from datetime import datetime

# === Fungsi Obfuscator ===
def obfuscate_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        original_code = f.read()
    encoded_code = base64.b64encode(original_code.encode()).decode()
    obfuscated_code = f"import base64\nexec(base64.b64decode('{encoded_code}'))"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(obfuscated_code)

def obfuscate_folder(input_folder, output_folder, log_callback, progress_callback, start_idx=0):
    os.makedirs(output_folder, exist_ok=True)
    py_files = [f for f in os.listdir(input_folder) if f.endswith('.py')]
    success, fail = 0, 0
    for idx, filename in enumerate(py_files, start=1):
        try:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            obfuscate_file(input_path, output_path)
            success += 1
            log_callback(f"✅ {filename} berhasil di-obfuscate")
        except Exception as e:
            fail += 1
            log_callback(f"❌ {filename} gagal: {type(e).__name__} - {str(e)}")
        progress_callback(start_idx + idx)
    return success, fail, len(py_files)

# === GUI ===
def run_obfuscation():
    paths = listbox.get(0, tk.END)
    if not paths:
        log("❌ Tidak ada file/folder untuk diproses !")
        return

    total_files = 0
    for p in paths:
        if os.path.isfile(p) and p.endswith(".py"):
            total_files += 1
        elif os.path.isdir(p):
            total_files += len([f for f in os.listdir(p) if f.endswith(".py")])

    processed = 0
    progress_bar.set(0)
    progress_bar.set(processed/total_files)

    for p in paths:
        if os.path.isfile(p) and p.endswith(".py"):
            try:
                out_file = p.replace(".py", "_obf.py")
                obfuscate_file(p, out_file)
                processed += 1
                progress_bar.set(processed/total_files)
                log(f"✅ File {os.path.basename(p)} obfuscated -> {out_file}")
            except Exception as e:
                log(f"❌ Error: {type(e).__name__} - {str(e)}")
                log(traceback.format_exc())
        elif os.path.isdir(p):
            out_folder = p + "_obf"
            try:
                success, fail, count = obfuscate_folder(
                    p, out_folder, log,
                    lambda idx: progress_bar.set((processed+idx)/total_files),
                    start_idx=processed
                )
                processed += count
                log(f"\n🎉 Folder {p} selesai: {success} sukses, {fail} gagal.")
                log(f"📂 Folder hasil: {out_folder}")
            except Exception as e:
                log(f"❌ Error: {type(e).__name__} - {str(e)}")
                log(traceback.format_exc())
        else:
            log(f"❌ Path tidak valid: {p}")

def drop(event):
    path = event.data.strip("{}")
    # Jika placeholder masih ada, hapus dulu
    if listbox.get(0) == "👉 drag n drop file / folder here":
        listbox.delete(0)
    listbox.insert(tk.END, path)

LOG_FILE = "obfuskit_log.txt"

def log(message):
    # Buat timestamp: contoh "2026-05-24 13:42:10"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"

    # Tampilkan di GUI
    result_box.configure(state="normal")
    result_box.insert(tk.END, line + "\n")
    result_box.see(tk.END)
    result_box.configure(state="disabled")

    # Simpan ke file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# === Fungsi Reset ===
def reset_list():
    listbox.delete(0, tk.END)
    listbox.insert(tk.END, "👉 drag n drop file / folder here")
    progress_bar.set(0)
    result_box.configure(state="normal")
    result_box.delete("1.0", tk.END)
    result_box.configure(state="disabled")
    log("🔄 Reset selesai, siap drag n drop file/folder baru")

# === Setup GUI ===
app = TkinterDnD.Tk()
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

app.title("Python Obfuscator GUI")
app.geometry("550x450")

listbox = tk.Listbox(app, height=6, selectmode=tk.MULTIPLE, font=("Arial", 10))
listbox.pack(fill="x", padx=10, pady=10)
listbox.insert(tk.END, "👉 drag n drop file / folder here")
listbox.drop_target_register(DND_FILES)
listbox.dnd_bind('<<Drop>>', drop)

ctk.CTkButton(app, text="Obfuscate Now", command=run_obfuscation, font=("Arial", 16, "bold")).pack(pady=10)
ctk.CTkButton(app, text="Reset", command=reset_list, font=("Arial", 14, "bold")).pack(pady=5)

progress_bar = ctk.CTkProgressBar(app, width=200, height=20)
progress_bar.pack(pady=10)
progress_bar.set(0)

result_box = tk.Text(app, height=20, wrap="word", state="disabled", font=("Arial", 10))
result_box.pack(fill="both", expand=True, padx=10, pady=10)

app.mainloop()
