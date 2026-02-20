# upload.py - upload out/YYYY-MM-DD/short.mp4 to YouTube using meta.json
import json
from datetime import datetime, timezone
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

ROOT = Path("C:/AXIS_YT")
CLIENT_SECRET = ROOT / "client_secret.json"
TOKEN = ROOT / "token.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]  # upload only


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_youtube():
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                raise FileNotFoundError(f"missing: {CLIENT_SECRET}")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            # local server auth (opens browser once)
            creds = flow.run_local_server(port=0)
        TOKEN.write_text(creds.to_json(), encoding="utf-8")

    return build("youtube", "v3", credentials=creds)


def upload_one(meta_path: Path) -> str:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    video_path = Path(meta["video"])

    if not video_path.exists():
        raise FileNotFoundError(f"video not found: {video_path}")

    # ---- dedupe guard (uploaded lock) ----
    uploaded_path = meta_path.parent / "uploaded.json"
    if uploaded_path.exists():
        uploaded = json.loads(uploaded_path.read_text(encoding="utf-8"))
        vid = uploaded.get("video_id") or meta.get("video_id")
        print("SKIP: already uploaded:", vid)
        return str(vid) if vid else ""

    # ---- build request ----
    title = (meta.get("title", video_path.stem) or video_path.stem)[:95]
    desc = meta.get("desc", "") or ""
    privacy = meta.get("privacy", "private")  # private/unlisted/public

    youtube = get_youtube()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": desc,
                "categoryId": "27",  # Education (safe default)
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print("Uploaded videoId:", video_id)

    # ---- write back results ----
    meta["video_id"] = video_id
    meta["uploaded_at_utc"] = utc_now_iso()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    uploaded_path.write_text(
        json.dumps(
            {
                "video_id": video_id,
                "uploaded_at_utc": meta["uploaded_at_utc"],
                "video": str(video_path),
                "meta": str(meta_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return video_id


def main():
    # latest meta.json by date folder (lexicographic works with YYYY-MM-DD)
    out_root = ROOT / "out"
    metas = sorted(out_root.glob("*/meta.json"))
    if not metas:
        raise FileNotFoundError("No meta.json found under out/*/meta.json. Run daily.py first.")
    latest = metas[-1]
    print("Using:", latest)
    upload_one(latest)


if __name__ == "__main__":
    main()
