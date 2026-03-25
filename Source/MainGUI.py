import customtkinter as ctk
from tkinter import filedialog
import threading
import time
import Backup
import Uploader
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SyncBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Backup Sentry")
        self.geometry("700x650")
        self.is_running = False

        # --- HEADER ---
        self.label = ctk.CTkLabel(self, text="YouTube Channel Backup", font=("Roboto", 24))
        self.label.pack(pady=10)

        # --- CONFIGURATION SECTION ---
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.pack(pady=10, padx=20, fill="x")

        # 1. Main Channel URL
        self.url_label = ctk.CTkLabel(self.config_frame, text="Main Channel URL (Source):")
        self.url_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.url_entry = ctk.CTkEntry(self.config_frame, width=400)
        self.url_entry.insert(0, "https://www.youtube.com/@thewhambammers6309/videos")
        self.url_entry.grid(row=0, column=1, padx=10, pady=5)

        # 2. Download Location
        self.path_label = ctk.CTkLabel(self.config_frame, text="Download Folder:")
        self.path_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.path_entry = ctk.CTkEntry(self.config_frame, width=400)
        self.path_entry.insert(0, r"C:\Users\stanl\Downloads")
        self.path_entry.grid(row=1, column=1, padx=10, pady=5)
        
        self.browse_btn = ctk.CTkButton(self.config_frame, text="Browse", width=80, command=self.browse_folder)
        self.browse_btn.grid(row=1, column=2, padx=10, pady=5)

        # 3. Backup Channel Auth
        self.auth_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.auth_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        self.login_button = ctk.CTkButton(
            self.auth_frame, 
            text="Login to YouTube", 
            command=self.run_login,
            fg_color="#c4302b" # YouTube Red
        )
        self.login_button.pack(side="left", padx=5)

        self.token_label = ctk.CTkLabel(self.auth_frame, text="Status: Checking...")
        self.token_label.pack(side="left", padx=10)
        self.update_token_status()

        # --- CONSOLE / LOGS ---
        self.console = ctk.CTkTextbox(self, width=650, height=200)
        self.console.pack(pady=10)

        # --- CONTROLS ---
        self.status_label = ctk.CTkLabel(self, text="Status: Idle", text_color="gray")
        self.status_label.pack(pady=5)

        self.start_button = ctk.CTkButton(self, text="Start Sentry Mode (24h)", command=self.toggle_sentry)
        self.start_button.pack(pady=5)

        self.sync_now_button = ctk.CTkButton(self, text="Manual Sync Now", fg_color="green", command=self.manual_sync)
        self.sync_now_button.pack(pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def log(self, message):
        self.console.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.console.see("end")

    def toggle_sentry(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.configure(text="Stop Sentry Mode", fg_color="red")
            self.status_label.configure(text="Status: Active (Sentry)", text_color="cyan")
            threading.Thread(target=self.sentry_loop, daemon=True).start()
        else:
            self.is_running = False
            self.start_button.configure(text="Start Sentry Mode (24h)", fg_color="#1f538d")
            self.status_label.configure(text="Status: Idle", text_color="gray")

    def sentry_loop(self):
        while self.is_running:
            self.run_sync_logic()
            self.log("Sleeping for 24 hours...")
            for _ in range(24 * 60): 
                if not self.is_running: return
                time.sleep(60)

    def manual_sync(self):
        threading.Thread(target=self.run_sync_logic, daemon=True).start()

    def update_token_status(self):
        """Updates the UI based on whether the login token exists."""
        if os.path.exists("token.pickle"):
            self.token_label.configure(text="? Authenticated", text_color="green")
            self.login_button.configure(text="Refresh Login", fg_color="gray")
        else:
            self.token_label.configure(text="? Not Logged In", text_color="orange")
            self.login_button.configure(text="Login to YouTube", fg_color="#c4302b")

    def run_login(self):
        """Runs the authentication in a separate thread so the GUI doesn't hang."""
        def auth_task():
            try:
                self.log("Opening browser for YouTube login...")
                Uploader.get_authenticated_service()
                self.log("Login Successful!")
                self.update_token_status()
            except Exception as e:
                self.log(f"Login Error: {e}")

        threading.Thread(target=auth_task, daemon=True).start()

    def run_sync_logic(self):
        # 1. Pull values from the GUI entries
        target_url = self.url_entry.get()
        save_path = self.path_entry.get()

        self.sync_now_button.configure(state="disabled")
        try:
            self.log(f"Syncing {target_url} to {save_path}...")
            
            # 2. Pass variables to your modules
            # Note: We need to tweak Backup.start_backup and Uploader.start_upload 
            # to accept these arguments!
            Backup.start_backup(target_url, save_path) 
            Uploader.start_upload(save_path)
            
            self.log("Cycle Complete!")
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.sync_now_button.configure(state="normal")

if __name__ == "__main__":
    app = SyncBotApp()
    app.mainloop()