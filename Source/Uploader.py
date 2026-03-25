import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pickle
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# --- CONFIGURATION ---
CLIENT_SECRETS_FILE = "client_secret.json"
DOWNLOADS_DIR = r"C:\Users\stanl\Downloads" #place where downloaded videos are stored
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"] #tells google we want "upload" permissions
HISTORY_FILE = "uploaded_log.txt"

def get_authenticated_service():
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            # This opens your browser. Log into the DESTINATION channel here.
            credentials = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def is_already_uploaded(video_title):
    if not os.path.exists(HISTORY_FILE):
        return False
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        uploaded_videos = f.read().splitlines()
    return video_title in uploaded_videos

def get_metadata(json_path):
    #reads the downloaded json file
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {
        "title": data.get("title", "Untitled Video"),
        "description": data.get("description", "Backup upload."),
        "tags": data.get("tags", [])
    }

def log_finished_upload(video_title):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(video_title + "\n")

def start_upload(DOWNLOADS_DIR=None, log_callback=None):
    print(f"Scanning folder: {DOWNLOADS_DIR}")

    def internal_log(msg):
        if log_callback: log_callback(msg)
        print(msg)

    internal_log(f"Scanning folder: {DOWNLOADS_DIR}")
    
    # Build the Google Service (Triggers Browser Login)
    youtube = get_authenticated_service()
    
    # 1. Loop through all files in your folder
    all_files = os.listdir(DOWNLOADS_DIR)
    
    for file in all_files:
        if file.endswith(".mp4"):
            # Get the name without the extension (e.g., 'Battlefield_Clip_01')
            base_name = os.path.splitext(file)[0]
            
            # Look for the matching .info.json
            json_path = os.path.join(DOWNLOADS_DIR, f"{base_name}.info.json")
            video_path = os.path.join(DOWNLOADS_DIR, file)

            if os.path.exists(json_path):
                meta = get_metadata(json_path)

                if is_already_uploaded(meta['title']):
                    print(f"Skipping {meta['title']} - already uploaded!")
                    continue
                
                # 2. Prepare the Data Payload
                body = {
                    "snippet": {
                        "title": meta['title'],
                        "description": meta['description'],
                        "tags": meta['tags'],
                        "categoryId": "20", # '20' is the Gaming category
                    },
                    "status": {
                        "privacyStatus": "private" # Keeping it private for the first test
                    }
                }

                print(f"--- STARTING UPLOAD: {meta['title']} ---")
                
                internal_log(f"--- STARTING UPLOAD: {meta['title']} ---")
                # 3. Prepare the File Stream
                media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)
                
                request = youtube.videos().insert(
                    part="snippet,status",
                    body=body,
                    media_body=media
                )
                
                # PROGRESS BAR LOGIC
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        print(f"Uploaded {int(status.progress() * 100)}%", end='\r')
                        # Update progress in GUI console
                        internal_log(f"Upload Progress: {int(status.progress() * 100)}%")
                
                log_finished_upload(meta['title'])
                internal_log(f"SUCCESS! Video ID: {response.get('id')}")
                print(f"\nSUCCESS! Video ID: {response.get('id')}")

if __name__ == "__main__":
    start_upload()

