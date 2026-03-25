import subprocess
import os
import sys

# --- HARDCODED DEFAULTS
# only used if the GUI doesn't provide different values
TARGET_URL = "https://www.youtube.com/@thewhambammers6309/videos"
SAVE_PATH = r"C:\Users\stanl\Downloads"

def start_backup(TARGET_URL=None, SAVE_PATH=None, log_callback=None):
    yt_dlp_exe = r"C:\Users\stanl\AppData\Local\Python\pythoncore-3.14-64\Scripts\yt-dlp.exe"
    ffmpeg_dir = r"C:\Program Files\ffmpeg\bin"
    archive_file = "downloaded_history.txt"

    command = [
        yt_dlp_exe, 
        "--ffmpeg-location", ffmpeg_dir,
        "--download-archive", archive_file,    #save data for what videos have been downloaded
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--write-info-json",
        "--newline", #Forces yt-dlp to output progress on new lines
        "-o", f"{SAVE_PATH}/%(title)s.%(ext)s",
        TARGET_URL
    ]
    print(f"Starting backup for: {TARGET_URL}")

    try:
        # Execute the process
        # Using subprocess.run ensures we wait for yt-dlp to finish before returning
        # We use Popen with stdout=PIPE to "catch" the text as it's generated
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1, 
            universal_newlines=True
        )

        for line in process.stdout:
            clean_line = line.strip()
            if clean_line:
                if log_callback:
                    log_callback(clean_line) # Sends to GUI
                else:
                    print(clean_line) # Fallback for standalone run

        process.wait()
        print("Success! Check your downloads folder.")
    except Exception as e:
        error_msg = f"Error in Downloader: {e}"
        if log_callback: log_callback(error_msg)
        print(error_msg)

if __name__ == "__main__":
    start_backup()