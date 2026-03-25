import Backup
import Uploader
import time

# 86400 seconds = 24 hours
SECONDS_IN_DAY = 86400 

def run_forever():
    print("--- YouTube Backup Bot: Sentry Mode Active ---")
    while True:
        try:
            print(f"\n[!] Starting Sync Cycle: {time.ctime()}")
            
            # Step 1: Check and Download
            # yt-dlp will automatically skip anything in 'downloaded_history.txt'
            Backup.start_backup() 
            
            # Step 2: Upload
            # Uploader will skip anything in 'uploaded_log.txt'
            Uploader.start_upload()
            
            print(f"\n[?] Sync Cycle Complete. Sleeping for 24 hours...")
            time.sleep(SECONDS_IN_DAY)
            
        except KeyboardInterrupt:
            print("\nShutting down Sentry Mode...")
            break
        except Exception as e:
            print(f"\n[X] Error during sync: {e}")
            print("Retrying in 1 hour...")
            time.sleep(3600)

if __name__ == "__main__":
    run_forever()