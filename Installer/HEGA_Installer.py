import os
import shutil
import tkinter as tk
import requests
import zipfile
from tkinter import messagebox, scrolledtext

def get_latest_assets():
    api_url = "https://api.github.com/repos/Lominub44/HEGA_TEST/releases/latest"
    response = requests.get(api_url).json()
    
    assets = []
    for asset in response.get("assets", []):
        assets.append((asset["name"], asset["browser_download_url"]))
    
    # Manually construct source code ZIP URL
    repo_zip_url = "https://github.com/Lominub44/HEGA_TEST/archive/refs/heads/main.zip"
    assets.append(("source_code.zip", repo_zip_url))
    
    if not assets:
        raise Exception("No assets found in the latest release.")
    
    return assets

def download_file(url, path):
    response = requests.get(url, stream=True)
    with open(path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)

def create_shortcut():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, "HEGA Launcher.lnk")
    exe_path = os.path.join(os.getenv("APPDATA"), "HEGA", "HEGA.Launcher.exe")
    
    with open(shortcut_path, "w") as f:
        f.write(f"Shortcut to {exe_path}")

def download_and_install():
    install_path = os.path.join(os.getenv("APPDATA"), "HEGA")
    
    try:
        if os.path.exists(install_path):
            shutil.rmtree(install_path)
        os.makedirs(install_path, exist_ok=True)
        
        assets = get_latest_assets()
        
        zip_path = None
        for name, url in assets:
            file_path = os.path.join(install_path, name)
            download_file(url, file_path)
            
            if name.lower().endswith(".zip"):
                zip_path = file_path
        
        if zip_path:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                extract_temp_path = os.path.join(install_path, "temp_extract")
                zip_ref.extractall(extract_temp_path)
            
            os.remove(zip_path)
            
            extracted_folder = None
            for folder in os.listdir(extract_temp_path):
                extracted_path = os.path.join(extract_temp_path, folder)
                if os.path.isdir(extracted_path):
                    extracted_folder = extracted_path
                    break
            
            if extracted_folder:
                for item in os.listdir(extracted_folder):
                    shutil.move(os.path.join(extracted_folder, item), install_path)
            
            shutil.rmtree(extract_temp_path)
        
        if shortcut_var.get():
            create_shortcut()
        
        messagebox.showinfo("Success", "HEGA Launcher has been installed successfully!")
    except Exception as e:
        messagebox.showerror("Installation Failed", str(e))

def show_disclaimer():
    disclaimer_window = tk.Toplevel(root)
    disclaimer_window.title("Privacy Policy & Legal Notice")
    disclaimer_window.geometry("500x400")
    
    text_area = scrolledtext.ScrolledText(disclaimer_window, wrap=tk.WORD, width=60, height=20)
    text_area.insert(tk.INSERT, "[Insert Privacy Policy & Legal Notice Here]")
    text_area.config(state=tk.DISABLED)
    text_area.pack(pady=10)
    
    accept_button = tk.Button(disclaimer_window, text="Accept", command=lambda: [disclaimer_window.destroy(), enable_install()])
    accept_button.pack(pady=5)

def enable_install():
    install_button.config(state=tk.NORMAL)

root = tk.Tk()
root.title("HEGA Launcher Setup Wizard")
root.geometry("400x250")

tk.Button(root, text="View Privacy Policy & Legal Notice", command=show_disclaimer).pack(pady=5)
shortcut_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Create Desktop Shortcut", variable=shortcut_var).pack(pady=5)

install_button = tk.Button(root, text="Install", command=download_and_install, state=tk.DISABLED)
install_button.pack(pady=20)

root.mainloop()
