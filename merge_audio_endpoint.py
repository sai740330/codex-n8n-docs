from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List
import requests
import os
import uuid
import subprocess

app = FastAPI()

class MergeAudioRequest(BaseModel):
    audio_files: List[HttpUrl]
    outputName: str

@app.post("/merge-audio")
def merge_audio(body: MergeAudioRequest):
    temp_dir = f"/tmp/{uuid.uuid4().hex}"
    os.makedirs(temp_dir, exist_ok=True)
    downloaded_files = []
    try:
        # Download each mp3
        for url in body.audio_files:
            file_path = os.path.join(temp_dir, os.path.basename(url))
            try:
                r = requests.get(str(url), timeout=10)
                r.raise_for_status()
            except requests.RequestException as e:
                raise HTTPException(status_code=400, detail=f"Failed to download {url}: {e}")
            with open(file_path, "wb") as f:
                f.write(r.content)
            downloaded_files.append(file_path)

        if not downloaded_files:
            raise HTTPException(status_code=400, detail="No audio files downloaded")

        # Prepare ffmpeg concat list file
        list_file = os.path.join(temp_dir, "files.txt")
        with open(list_file, "w") as lf:
            for path in downloaded_files:
                lf.write(f"file '{path}'\n")

        os.makedirs("merged", exist_ok=True)
        output_path = os.path.abspath(os.path.join("merged", body.outputName))

        cmd = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file,
            "-c",
            "copy",
            output_path,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"ffmpeg failed: {e.stderr.decode()}")

        return {"status": "success", "merged_audio_file": output_path}
    finally:
        # Cleanup downloaded files
        for path in downloaded_files:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(list_file):
            os.remove(list_file)
        if os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass

