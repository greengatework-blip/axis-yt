from __future__ import annotations
import os
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

ROOT = Path(__file__).resolve().parent
SECRETS_DIR = ROOT / "secrets"
CLIENT_SECRET = SECRETS_DIR / "client_secret.json"
TOKEN_PATH = SECRETS_DIR / "token.json"

def get_youtube():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                raise FileNotFoundError(f"Missing {CLIENT_SECRET}. Put OAuth client secret there.")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)

def upload_video(video_path: Path, title: str, description: str = "", tags=None, category_id="22", privacy_status="private"):
    youtube = get_youtube()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id,
        },
        "status": {"privacyStatus": privacy_status},
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"Upload: {int(status.progress()*100)}%")
    print("Uploaded:", resp.get("id"))
    return resp.get("id")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--desc", default="")
    p.add_argument("--privacy", default="private", choices=["private","unlisted","public"])
    args = p.parse_args()

    vid = Path(args.video)
    upload_video(vid, args.title, args.desc, privacy_status=args.privacy)