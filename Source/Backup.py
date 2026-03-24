import subprocess
import os

# --- CONFIGURATION ---
TARGET_URL = "https://www.youtube.com/@thewhambammers6309/videos"
SAVE_PATH = r"C:\Users\stanl\Downloads"

def start_backup():
    yt_dlp_exe = r"C:\Users\stanl\AppData\Local\Python\pythoncore-3.14-64\Scripts\yt-dlp.exe"
    ffmpeg_dir = r"C:\Program Files\ffmpeg\bin"
    command = [
        yt_dlp_exe, 
        "--ffmpeg-location", ffmpeg_dir,
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--write-info-json",
        #"-f", "bestvideo+bestaudio/best", 
        "-o", f"{SAVE_PATH}/%(title)s.%(ext)s",
        TARGET_URL
    ]
    print("Starting highquality backup")

    try:
        subprocess.run(command, check=True)
        print("Success! Check your downloads folder.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_backup()