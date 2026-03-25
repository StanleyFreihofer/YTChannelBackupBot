import subprocess
import os

# --- HARDCODED DEFAULTS
# only used if the GUI doesn't provide different values
TARGET_URL = "https://www.youtube.com/@thewhambammers6309/videos"
SAVE_PATH = r"C:\Users\stanl\Downloads"

def start_backup(TARGET_URL=None, SAVE_PATH=None):
    yt_dlp_exe = r"C:\Users\stanl\AppData\Local\Python\pythoncore-3.14-64\Scripts\yt-dlp.exe"
    ffmpeg_dir = r"C:\Program Files\ffmpeg\bin"
    archive_file = "downloaded_history.txt"

    command = [
        yt_dlp_exe, 
        "--ffmpeg-location", ffmpeg_dir,
        "--download-archive", archive_file,    #save data for what videos have been downloaded
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--write-info-json",
        #"-f", "bestvideo+bestaudio/best", 
        "-o", f"{SAVE_PATH}/%(title)s.%(ext)s",
        TARGET_URL
    ]
    print(f"Starting backup for: {TARGET_URL}")

    try:
        # Execute the process
        # Using subprocess.run ensures we wait for yt-dlp to finish before returning
        subprocess.run(command, check=True)
        print("Success! Check your downloads folder.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_backup()