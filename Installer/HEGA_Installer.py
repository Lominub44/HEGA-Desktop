import os
import stat
import shutil
import psutil
import ctypes
import sys
import zipfile
import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from pathlib import Path
import winshell
from win32com.client import Dispatch

def run_as_admin():
    """Request admin rights if not already running as admin."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# Request admin rights at the start
run_as_admin()

def kill_process_by_name(name):
    """Kill the process if it's running."""
    for process in psutil.process_iter(attrs=["pid", "name"]):
        if process.info["name"] == name:
            try:
                process.terminate()
                process.wait(timeout=5)
            except psutil.NoSuchProcess:
                pass
            except psutil.AccessDenied:
                messagebox.showerror("Error", f"Cannot close {name}. Close it manually.")

def get_latest_assets():
    api_url = "https://api.github.com/repos/Lominub44/HEGA_TEST/releases/latest"
    response = requests.get(api_url).json()
    
    assets = [(asset["name"], asset["browser_download_url"]) for asset in response.get("assets", [])]
    assets.append(("source_code.zip", "https://github.com/Lominub44/HEGA_TEST/archive/refs/heads/main.zip"))
    
    if not assets:
        raise Exception("No assets found in the latest release.")
    
    return assets

def download_file(url, path):
    """Download file from URL to a specific path."""
    response = requests.get(url, stream=True)
    with open(path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)

def create_shortcut():
    """Create a desktop shortcut for HEGA Launcher."""
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, "HEGA Launcher.lnk")
    target = os.path.join(os.getenv("APPDATA"), "HEGA", "HEGA.Launcher.exe")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.IconLocation = target
    shortcut.save()

def update_status(message, progress_value=None):
    status_label.config(text=message)
    if progress_value is not None:
        progress_bar['value'] = progress_value
    root.update_idletasks()

def download_and_install():
    install_path = os.path.join(os.getenv("APPDATA"), "HEGA")
    launcher_path = os.path.join(install_path, "HEGA.Launcher.exe")

    try:
        update_status("Closing existing processes...")
        kill_process_by_name("HEGA.Launcher.exe")  # Close launcher if running
        
        if os.path.exists(launcher_path):  # Remove read-only flag if needed
            os.chmod(launcher_path, stat.S_IWRITE)
            os.remove(launcher_path)

        if os.path.exists(install_path):  # Delete old installation
            shutil.rmtree(install_path)
        os.makedirs(install_path, exist_ok=True)

        assets = get_latest_assets()
        zip_path = None
        total_steps = len(assets) + 3  # Number of steps in progress
        step = 0

        for name, url in assets:
            step += 1
            update_status(f"Downloading {name}...", (step / total_steps) * 100)
            file_path = os.path.join(install_path, name)
            download_file(url, file_path)
            
            if name.lower().endswith(".zip"):
                zip_path = file_path

        if zip_path:
            update_status("Extracting files...", (step / total_steps) * 100)
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
            update_status("Creating desktop shortcut...", (step / total_steps) * 100)
            create_shortcut()
        
        update_status("Installation complete!", 100)
        messagebox.showinfo("Success", "HEGA Launcher has been installed successfully!")

    except Exception as e:
        messagebox.showerror("Installation Failed", str(e))

def show_disclaimer():
    """Display the Privacy Policy & Legal Notice before allowing installation."""
    disclaimer_window = tk.Toplevel(root)
    disclaimer_window.title("Privacy Policy & Legal Notice")
    disclaimer_window.geometry("500x400")

    text_area = scrolledtext.ScrolledText(disclaimer_window, wrap=tk.WORD, width=60, height=20)
    text_area.insert(tk.INSERT, """Privacy Policy
==============

We take care about the protection of your personal data. The following statement informs you about which personal data we collect and how we process and use it.
This is a translated version of our German privacy document. In the event of interpretational questions, the German version shall remain authoritative.

Subject of this Privacy Policy
------------------------------
This privacy policy applies to all services associated with Hidden Empire, including the desktop port of the game Hidden Empire. This privacy policy exclusively governs how Hidden Empire handles your data.
Should you use third-party services in conjunction with our game, their respective privacy terms will apply.
Hidden Empire does not review the data protection conditions of these third parties.

Access Data Without Personal Reference
----------------------------------------
When you launch and play the game, we automatically collect certain data transmitted by your device to our servers (so-called server log files). This data includes the following:
 - IP address
 - Date and time of the request
 - Time zone difference to Greenwich Mean Time (GMT)
 - Content of the request (e.g., game action or specific in-game activity)
 - Access status/HTTP status code (if applicable)
 - Amount of data transferred in each instance
 - Referring source (if applicable)
 - Operating system and its interface
 - Language and version of the system software (if applicable)

The processing is carried out in accordance with Art. 6 para. 1 lit. f DSGVO (German data protection law) based on our legitimate interest in improving the stability and functionality of our game.
The collected data is not passed on or otherwise used.
However, we reserve the right to review the server log files retrospectively should concrete evidence of illegal usage arise.

Collection and Processing of Personal Data
--------------------------------------------
Personal data is only collected if you voluntarily provide it.
During registration or account creation within the game, the following personal data is collected:
 - Email address
 - Year of birth
These data are linked to a personal account comprising a username and password.
All provided personal data will be stored in compliance with the provisions of the Federal Data Protection Act and the Telemedia Act, and will be treated confidentially.

Use and Disclosure of Personal Data
-------------------------------------
The personal data we collect is necessary for the use of our game.
We do not transfer personal data to third parties.

Data Collection Policy for the Desktop Application
---------------------------------------------------
The desktop application of Hidden Empire itself does not collect, store, or process any personal or non-personal data. All desktop application functionalities operate locally on your device. However, within the desktop application, an integrated website is running, which may collect and process data as outlined in this privacy policy. This means that while the desktop application does not perform data collection, the web-based features embedded in it are subject to the same data collection practices as when accessed directly via a browser.


Data Security
-------------
We process the information we collect in accordance with German data protection law.
All employees are bound by data confidentiality and data protection regulations and have been duly instructed.
Data transmitted via our game is encrypted using SSL or equivalent encryption methods.

Cookies
-------
Our game may use cookies or similar local storage techniques to enable certain in-game functions.
Cookies are small text files stored on your device. They contain only the information that we send to your device—no private data can be read from them.
Cookies require only a minimal amount of storage space, do not impair the functioning of your device, and do not contain personal data.
If you revisit the game, cookies enable your device to be recognized, ensuring, among other things, that your game session can be properly maintained.
We use cookies that are automatically deleted from your system after you close the game or after a maximum period of 7 days.
You may opt to have cookies stored persistently (for functions such as auto-login).

You can adjust your device or application settings to disable cookies at any time.
However, please note that this may prevent you from using the game to its full extent.

Use of Game Statistics (Matomo)
-------------------------------
Our game uses Matomo (formerly Piwik), an open-source software for statistical analysis of user access.
Matomo utilizes cookies or similar techniques—small text files stored on your device—to analyze user interaction within the game.
Information generated by these storage techniques regarding your gameplay is stored on the provider's server in Germany.
The IP address is anonymized immediately after processing and prior to storage.
While you may refuse the use of these storage techniques through your device settings, note that this may restrict full access to the game’s functionalities.

Information, Correction, Blocking, and Deletion
-------------------------------------------------
You have the right to obtain information about your stored personal data at any time.
In addition, you have the right to request corrections or deletion of your personal data.
If deletion conflicts with legal or contractual retention obligations, we will block the data instead.

Contact
-------
For further questions regarding data protection, or for requests to obtain, correct, or delete your data, please contact us at:
datenschutz@hiddenempire.de

Disclaimer
==========

Hidden Empire - Galaxy Adventures is a non-commercial fan production. All Star Wars materials used on this site in the form of images, names, and other media are subject to the copyright of Lucasfilm Ltd.
Star Wars is a registered trademark and is presented on the internet through the official StarWars.com website.
The use of protected materials in Hidden Empire Galaxy Adventures does not pursue any financial interests but serves a documentary purpose.

Star Wars, the Star Wars logo, all names and pictures of Star Wars characters, vehicles, and any other Star Wars-related items are registered trademarks and/or copyrights of Lucasfilm Ltd., or their respective trademark and copyright holders. This website is a non-commercial fan project.

Imprint
-------
Contact: Webmaster (no support)  
hiddenempire.de  
c/o Marcus Pekar  
Storkower Str. 2A  
15713 Königs Wusterhausen  
Germany  
E-Mail: webmaster@hiddenempire.de

Contact: Support & Help  
E-Mail: support@hiddenempire.de 

Support for external matters only. For internal game problems and questions please use the ticket system within the game or the forum. Note: Email support is not staffed daily.

"Thank you to everyone who helped build and develop this project!"

Liability for Links
--------------------
In the case of direct or indirect references to external websites ("links") that are outside the author's area of responsibility, liability would only come into effect if the author was aware of the content and it was technically possible and reasonable to prevent use in the event of illegal content. The author hereby expressly declares that no illegal content was discernible on the linked pages at the time the link was created. The author has no influence whatsoever on the current and future design, the content, or the authorship of the linked/connected pages. He therefore hereby expressly distances himself from all content on all linked/connected pages that were changed after the link was created. This statement applies to all links and references set within our own website as well as to third-party entries in the forum set up by the author. The provider of the page to which reference was made is solely liable for illegal, incorrect, or incomplete content and in particular for damage resulting from the use or non-use of such information, not the person who merely refers to the respective publication via links.

Hiddenempire.de is a project by Star Wars fans. We are not a company and therefore not registered in any register. Any advertising that appears and donations are used exclusively to finance the server. The source code of this project is, unless otherwise indicated, under the copyright of our programmers.
""")
    text_area.config(state=tk.DISABLED)
    text_area.pack(pady=10)

    accept_button = tk.Button(disclaimer_window, text="Accept", command=lambda: [disclaimer_window.destroy(), enable_install()])
    accept_button.pack(pady=5)

def enable_install():
    """Enable the install button after accepting the disclaimer."""
    install_button.config(state=tk.NORMAL)

# Run installer UI
root = tk.Tk()

root.title("HEGA Launcher Setup Wizard")
root.geometry("400x350")

tk.Button(root, text="View Privacy Policy & Legal Notice", command=show_disclaimer).pack(pady=5)

shortcut_var = tk.BooleanVar()
tk.Checkbutton(root, text="Create a desktop shortcut", variable=shortcut_var).pack(pady=5)

install_button = tk.Button(root, text="Install", command=download_and_install, state=tk.DISABLED)
install_button.pack(pady=10)

status_label = tk.Label(root, text="Waiting for installation...")
status_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
progress_bar.pack(pady=5)

root.mainloop()
