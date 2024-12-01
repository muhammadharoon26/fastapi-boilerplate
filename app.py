# from typing import Union

# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import time

app = FastAPI()

class YouTubeDownloader:
    def __init__(self, base_url="https://yt5s.biz/mates/en/convert", max_retries=3):
        self.base_url = base_url
        self.max_retries = max_retries
        self.headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://yt5s.biz",
            "referer": "https://yt5s.biz/enxj101/",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        self.formats = {
            "mp3_128k": {"ext": "mp3", "note": "128k", "format": None, "download_key": "downloadUrlX"},
            "mp4_360p": {"ext": "mp4", "note": "360p", "format": "134", "download_key": "downloadUrlX"},
            "mp4_720p": {"ext": "mp4", "note": "720p", "format": "136", "download_key": "downloadUrlX"},
            "mp4_1080p": {"ext": "mp4", "note": "1080p60", "format": "299", "download_key": "downloadUrlX"},
        }

    def download(self, video_url, video_id, title, format_key):
        if format_key not in self.formats:
            return None
        
        format_config = self.formats[format_key]
        download_key = format_config["download_key"]

        for attempt in range(1, self.max_retries + 1):
            try:
                payload = {
                    "id": video_id,
                    "platform": "youtube",
                    "url": video_url,
                    "title": title,
                    "ext": format_config["ext"],
                    "note": format_config["note"],
                    "format": format_config["format"] or "",
                }
                self.headers["x-note"] = format_config["note"]
                response = requests.post(self.base_url, headers=self.headers, data=payload)
                response_json = response.json()

                if response_json.get("status") == "success" and download_key in response_json:
                    return response_json[download_key]
            except Exception:
                pass

            # Back-off strategy for retries
            time.sleep(2 * attempt)  # Increase delay with attempts
        return None

class VideoRequest(BaseModel):
    video_url: str
    title: str

@app.post("/download/")
async def download_video(request: VideoRequest):
    downloader = YouTubeDownloader()
    video_id = "ypwjF/ZPYN6kI06qjQn2C7dtkDtfZwhwUux5GAgxRbSUbEYH92ehW+4bV8+cy37Q4OAPwxKFOPwWgTuS93pyvCWeopjS4wKyMIpreLr4+O0="
    formats_to_try = ["mp3_128k", "mp4_360p", "mp4_720p", "mp4_1080p"]

    results = {}
    for format_key in formats_to_try:
        download_url = downloader.download(request.video_url, video_id, request.title, format_key)
        results[format_key] = download_url or ""

    if all(not url for url in results.values()):
        raise HTTPException(status_code=500, detail="Failed to generate download URLs")

    return results