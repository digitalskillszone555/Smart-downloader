import os
import re
import requests
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Optional, Callable

import streamlit as st
from yt_dlp import YoutubeDL

# Premium User-Agent for modern browser simulation
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed and accessible in the system PATH."""
    return shutil.which("ffmpeg") is not None

@st.cache_resource(ttl=86400)
def ensure_latest_engine():
    """Silently update yt-dlp safely."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "yt-dlp", "--quiet"],
            capture_output=True,
            timeout=15,
            check=False
        )
    except Exception:
        pass

def get_downloads_dir() -> Path:
    """Uses a strictly defined local directory to prevent path traversal."""
    base = Path(os.path.expanduser("~")).resolve() / "Downloads" / "SmartDownloader"
    base.mkdir(parents=True, exist_ok=True)
    return base

def _sanitize_filename(name: str) -> str:
    """SecOps Hardening: Removes any characters that could allow path traversal or shell injection."""
    clean = re.sub(r'[^\w\-_.]', '_', name)
    # Prevent hidden files or directory climbing
    clean = clean.lstrip('.')
    return clean if clean else "downloaded_media"

def _get_common_opts(downloads_dir: Path, progress_hook: Optional[Callable] = None):
    return {
        "outtmpl": str(downloads_dir / "%(title).80s_%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "user_agent": USER_AGENT,
        "restrictfilenames": True, # Prevents spaces and weird chars in filenames
        "age_limit": 17,
        "geo_bypass": True,
        "noprogress": True,
    }

def download_video(url: str, quality_label: str, progress_hook: Optional[Callable] = None) -> Path:
    downloads_dir = get_downloads_dir()
    height_map = {"4K (2160p)": 2160, "2K (1440p)": 1440, "1080p": 1080, "720p": 720, "480p": 480, "360p": 360}
    target_h = height_map.get(quality_label, 1080)

    opts = _get_common_opts(downloads_dir, progress_hook)
    opts.update({
        "format": f"bestvideo[height<={target_h}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={target_h}]+bestaudio/best[height<={target_h}]/best",
        "format_sort": ["res", "ext:mp4:m4a"],
        "merge_output_format": "mp4",
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
    })

    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return Path(ydl.prepare_filename(info)).with_suffix(".mp4")

def download_audio(url: str, quality_kbps: str = "320", progress_hook: Optional[Callable] = None) -> Path:
    downloads_dir = get_downloads_dir()
    kbps = quality_kbps.split("k")[0] if "k" in quality_kbps else "320"
    
    opts = _get_common_opts(downloads_dir, progress_hook)
    opts.update({
        "format": "bestaudio/best",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": kbps}],
    })

    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return Path(ydl.prepare_filename(info)).with_suffix(".mp3")

def download_image(url: str, progress_callback: Optional[Callable] = None) -> Path:
    downloads_dir = get_downloads_dir()
    
    try:
        with YoutubeDL({"quiet": True, "skip_download": True, "user_agent": USER_AGENT}) as ydl:
            info = ydl.extract_info(url, download=False)
            img_url = info.get("url") if info.get("ext") in ["jpg", "png", "webp", "jpeg"] else info.get("thumbnail")
            img_url = img_url or url
    except:
        img_url = url

    response = requests.get(img_url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=20)
    response.raise_for_status()
    
    content_type = response.headers.get("Content-Type", "").lower()
    ext = ".jpg"
    if "png" in content_type: ext = ".png"
    elif "webp" in content_type: ext = ".webp"
    
    # SecOps Sanitization
    raw_name = img_url.split('/')[-1].split('?')[0]
    safe_name = _sanitize_filename(raw_name)
    
    save_path = (downloads_dir / f"{safe_name}{ext}").resolve()
    
    # Verify the path is still inside the intended directory (Path Traversal Protection)
    if not str(save_path).startswith(str(downloads_dir)):
        raise PermissionError("Suspicious file path detected.")

    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=16384):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total_size > 0:
                    progress_callback(downloaded / total_size)
            
    return save_path
