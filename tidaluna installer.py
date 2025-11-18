import customtkinter as ctk
import os
import shutil
import zipfile
import requests
import threading
import platform
import subprocess
import time
import sys

# --- [UI STYLING & THEME] ---
class Theme:
    MAIN_BG = "#000000"
    CONTAINER_BG = "#121212"
    WIDGET_BG = "#1c1c1c"
    ACTIVE_BUTTON = "#e5e5e5"
    INACTIVE_PILL = "#282828"
    PROGRESS_COLOR = "#ffffff"  # White for OLED contrast
    
    # Button Styles
    BUTTON_START_ENABLED_FG = "#383838"
    BUTTON_START_ENABLED_HOVER = "#484848"
    BUTTON_DISABLED_FG = "#1c1c1c"
    
    # Destructive/Uninstall Styles
    BUTTON_CANCEL_ENABLED_FG = "#9e2a2b"
    BUTTON_CANCEL_ENABLED_HOVER = "#802122"
    
    # Text
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#8e8e8e"
    TEXT_ON_ACTIVE = "#000000"
    TEXT_DISABLED = "#4d4d4d"
    
    # Fonts
    FONT_HEADER = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 13, "normal")
    FONT_SMALL = ("Segoe UI", 11, "normal")
    FONT_MONO = ("Consolas", 11, "normal")

# --- [CONFIGURATION] ---
GITHUB_REPO = "Inrixia/TidaLuna"
GITHUB_API_LATEST = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class TidaLunaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("TidaLuna Manager")
        self.geometry("550x550")
        self.configure(fg_color=Theme.MAIN_BG)
        self.resizable(False, False)
        
        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # State
        self.is_running = False

        # --- UI Construction ---
        self.create_header()
        self.create_log_panel()
        self.create_progress_panel()
        self.create_action_panel()
        
        self.log("Ready. Select an option below.")

    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 10))
        
        title = ctk.CTkLabel(
            header_frame, 
            text="TIDALUNA MANAGER", 
            font=("Segoe UI", 20, "bold"), 
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(side="left")
        
        version = ctk.CTkLabel(
            header_frame, 
            text="v1.2 - Visiuun <3", 
            font=Theme.FONT_SMALL, 
            text_color=Theme.TEXT_SECONDARY
        )
        version.pack(side="left", padx=(10, 0), pady=(5, 0))

    def create_log_panel(self):
        # Label
        ctk.CTkLabel(
            self, 
            text="ACTIVITY LOG", 
            font=Theme.FONT_HEADER, 
            text_color=Theme.TEXT_SECONDARY, 
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=25, pady=(70, 5)) # Offset for absolute header

        # Container
        self.log_container = ctk.CTkFrame(self, fg_color=Theme.CONTAINER_BG, corner_radius=10)
        self.log_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.log_container.grid_columnconfigure(0, weight=1)
        self.log_container.grid_rowconfigure(0, weight=1)

        # Textbox
        self.log_box = ctk.CTkTextbox(
            self.log_container, 
            font=Theme.FONT_MONO,
            fg_color="transparent",
            text_color=Theme.TEXT_PRIMARY,
            state="disabled",
            wrap="word"
        )
        self.log_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def create_progress_panel(self):
        self.status_label = ctk.CTkLabel(
            self, 
            text="Status: Idle", 
            font=Theme.FONT_BODY, 
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        )
        self.status_label.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(
            self, 
            height=4, 
            corner_radius=2, 
            progress_color=Theme.PROGRESS_COLOR, 
            fg_color=Theme.INACTIVE_PILL
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

    def create_action_panel(self):
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 30))
        action_frame.grid_columnconfigure((0, 1), weight=1)

        # Install Button
        self.install_btn = ctk.CTkButton(
            action_frame, 
            text="INSTALL / UPDATE", 
            font=(Theme.FONT_BODY[0], 13, "bold"),
            height=45,
            fg_color=Theme.BUTTON_START_ENABLED_FG, 
            hover_color=Theme.BUTTON_START_ENABLED_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            command=lambda: self.start_thread(self.run_install_logic)
        )
        self.install_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Uninstall Button
        self.uninstall_btn = ctk.CTkButton(
            action_frame, 
            text="UNINSTALL", 
            font=(Theme.FONT_BODY[0], 13, "bold"),
            height=45,
            fg_color=Theme.BUTTON_DISABLED_FG, 
            hover_color=Theme.BUTTON_CANCEL_ENABLED_HOVER, # Red on hover
            text_color=Theme.TEXT_SECONDARY,
            command=lambda: self.start_thread(self.run_uninstall_logic)
        )
        self.uninstall_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))

    # --- [LOGIC & UTILS] ---

    def log(self, message):
        """Thread-safe logging with style."""
        self.after(0, lambda: self._log_internal(message))

    def _log_internal(self, message):
        self.log_box.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        print(message)

    def update_status(self, text):
        self.after(0, lambda: self.status_label.configure(text=f"Status: {text}"))

    def update_progress(self, val):
        self.after(0, lambda: self.progress_bar.set(val))

    def toggle_controls(self, state):
        """Enable/Disable buttons during operations."""
        s = "normal" if state else "disabled"
        self.is_running = not state
        self.install_btn.configure(state=s)
        self.uninstall_btn.configure(state=s)

    def start_thread(self, target):
        if self.is_running: return
        self.toggle_controls(False)
        self.update_progress(0)
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    # --- [CORE FUNCTIONALITY] ---

    def kill_tidal(self):
        self.log("Force stopping TIDAL process...")
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(["taskkill", "/F", "/IM", "TIDAL.exe"], 
                               creationflags=0x08000000, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            else:
                subprocess.run(["pkill", "-f", "TIDAL"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["pkill", "-f", "tidal"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            time.sleep(1.5)
        except:
            pass

    def get_tidal_resources_path(self):
        os_name = platform.system()
        if os_name == "Windows":
            local_app_data = os.getenv('LOCALAPPDATA')
            tidal_base = os.path.join(local_app_data, 'TIDAL')
            if not os.path.exists(tidal_base): raise Exception("TIDAL installation not found.")

            # Version Sorting (2.39 > 2.9)
            def get_ver(name):
                try: return tuple(map(int, name.replace("app-", "").split('.')))
                except: return (0, 0, 0)

            subdirs = [d for d in os.listdir(tidal_base) if d.startswith("app-") and os.path.isdir(os.path.join(tidal_base, d))]
            if not subdirs: raise Exception("No app-x.x.x folder found.")
            
            latest_version_dir = sorted(subdirs, key=get_ver, reverse=True)[0]
            self.log(f"Detected Version: {latest_version_dir}")
            return os.path.join(tidal_base, latest_version_dir, "resources")

        elif os_name == "Darwin": return "/Applications/TIDAL.app/Contents/Resources"
        elif os_name == "Linux": return "/opt/tidal-hifi/resources"
        else: raise Exception("Unsupported Operating System")

    def run_install_logic(self):
        try:
            self.kill_tidal()
            self.update_status("Locating Directories...")
            self.update_progress(0.1)
            
            resources_path = self.get_tidal_resources_path()
            
            # Download
            self.update_status("Fetching Release Info...")
            self.log("Contacting GitHub API...")
            resp = requests.get(GITHUB_API_LATEST)
            if resp.status_code != 200: raise Exception(f"GitHub API Error: {resp.status_code}")
            
            data = resp.json()
            tag = data.get("tag_name", "unknown")
            self.log(f"Latest Luna Version: {tag}")
            
            assets = data.get("assets", [])
            download_url = next((a["browser_download_url"] for a in assets if a["name"] == "luna.zip"), None)
            if not download_url: raise Exception("luna.zip missing from release.")

            self.update_status(f"Downloading {tag}...")
            self.update_progress(0.3)
            r = requests.get(download_url)
            
            temp_zip = os.path.join(os.getcwd(), "luna_temp.zip")
            with open(temp_zip, 'wb') as f: f.write(r.content)
            self.log("Download complete.")

            # Install
            self.update_status("Installing Files...")
            self.update_progress(0.6)
            
            app_asar = os.path.join(resources_path, "app.asar")
            original_asar = os.path.join(resources_path, "original.asar")
            luna_app_folder = os.path.join(resources_path, "app")

            if os.path.exists(app_asar):
                if not os.path.exists(original_asar):
                    self.log("Creating backup of original TIDAL...")
                    os.rename(app_asar, original_asar)
            elif not os.path.exists(original_asar):
                raise Exception("Critical: app.asar not found.")

            if os.path.exists(luna_app_folder):
                self.log("Cleaning old installation...")
                shutil.rmtree(luna_app_folder)
            
            self.log("Extracting new files...")
            with zipfile.ZipFile(temp_zip, 'r') as z:
                z.extractall(luna_app_folder)
            
            os.remove(temp_zip)

            # Mac Fix
            if platform.system() == "Darwin":
                self.log("Applying macOS CodeSign fix...")
                subprocess.run(["codesign", "--force", "--deep", "--sign", "-", "/Applications/TIDAL.app"])

            self.update_progress(1.0)
            self.update_status("Complete")
            self.log("SUCCESS: Luna has been installed.")
            self.log("You may now open TIDAL.")

        except Exception as e:
            self.update_progress(0)
            self.update_status("Error")
            self.log(f"ERROR: {e}")
        finally:
            self.toggle_controls(True)

    def run_uninstall_logic(self):
        try:
            self.kill_tidal()
            self.update_status("Locating...")
            self.update_progress(0.2)
            
            resources_path = self.get_tidal_resources_path()
            luna_app_folder = os.path.join(resources_path, "app")
            original_asar = os.path.join(resources_path, "original.asar")
            app_asar = os.path.join(resources_path, "app.asar")

            self.log("Removing Luna modifications...")
            if os.path.exists(luna_app_folder):
                shutil.rmtree(luna_app_folder)
            
            self.update_progress(0.6)
            
            if os.path.exists(original_asar):
                if os.path.exists(app_asar): os.remove(app_asar)
                os.rename(original_asar, app_asar)
                self.log("Restored original TIDAL core.")
            else:
                self.log("Warning: Original backup not found.")

            self.update_progress(1.0)
            self.update_status("Uninstalled")
            self.log("SUCCESS: TidaLuna has been uninstalled.")

        except Exception as e:
            self.update_progress(0)
            self.update_status("Error")
            self.log(f"ERROR: {e}")
        finally:
            self.toggle_controls(True)

if __name__ == "__main__":
    app = TidaLunaApp()
    app.mainloop()