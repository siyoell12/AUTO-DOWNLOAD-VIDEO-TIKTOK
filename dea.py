#!/usr/bin/env python3
"""
mass_tiktok_downloader_with_watermark.py
- Membaca urls.txt (1 URL per baris)
- Mengunduh video TikTok (hd preference) menggunakan yt-dlp
- Menambahkan watermark teks (nama Anda) di sebelah kiri (vertikal tengah) menggunakan ffmpeg
- Menjalankan beberapa download paralel
"""

import asyncio
import subprocess
import shutil
from pathlib import Path
import argparse
import sys
import os

# ---------- CONFIG ----------
URLS_FILE = Path("urls.txt")
OUTPUT_DIR = Path("downloads")
TEMP_DIR = Path("tmp_downloads")
CONCURRENT = 3          # proses paralel
RETRIES = 3
YT_DLP_CMD = shutil.which("yt-dlp") or "yt-dlp"
FFMPEG_CMD = shutil.which("ffmpeg") or "ffmpeg"

# yt-dlp format: usahakan video >=720p + audio, fallback best
FORMAT = "bv*[height>=720]+ba/best"

# template output dari yt-dlp (sementara ke tmp file, extension asli)
YT_DLP_OUT_TEMPLATE = "%(uploader)s/%(id)s.%(ext)s"

# final output struktur
FINAL_OUT_BASE = OUTPUT_DIR / "watermarked"  # final: downloads/watermarked/<uploader>/<id>.mp4

# extra yt-dlp options
EXTRA_OPTS = [
    "--no-playlist",
    "--restrict-filenames",
    "--continue",
    "--no-warnings",
    "--merge-output-format", "mp4",
]

# ---------- HELPERS ----------
def find_font_path():
    """
    Try several common font paths. Return fontfile path or None.
    """
    candidates = []
    if sys.platform.startswith("win"):
        windir = os.environ.get("WINDIR", r"C:\Windows")
        candidates += [
            os.path.join(windir, "Fonts", "arial.ttf"),
            os.path.join(windir, "Fonts", "calibri.ttf"),
            os.path.join(windir, "Fonts", "seguiemj.ttf"),
        ]
    elif sys.platform == "darwin":
        candidates += [
            "/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSDisplay.ttf",
        ]
    else:
        # linux common
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]

    for c in candidates:
        if os.path.exists(c):
            return c
    return None

async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    out, _ = await proc.communicate()
    return proc.returncode, (out.decode(errors="ignore") if out else "")

async def add_watermark(input_path: Path, output_path: Path, watermark_text: str, fontfile: str = None,
                    fontsize:int=36, padding:int=10):
    """
    uses ffmpeg drawtext to overlay watermark_text on left side (vertical center).
    output_path parent must exist.
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build drawtext filter with proper escaping
    # Escape special characters in the text
    escaped_text = watermark_text.replace("'", "\\'").replace(":", "\\:")
    
    # Handle font path - use proper escaping
    if fontfile:
        # Use proper escaping for font path
        fontfile_escaped = fontfile.replace("\\", "/").replace(":", "\\:")
        font_part = f"fontfile='{fontfile_escaped}'"
    else:
        font_part = "font='Arial'"

    # Construct the filter with proper syntax
    drawtext = (
        f"{font_part}:text='{escaped_text}'"
        f":fontsize={fontsize}:fontcolor=white"
        f":box=1:boxcolor=black@0.5:boxborderw=8"
        f":x={padding}:y=(h-text_h)/2"
    )

    cmd = [
        FFMPEG_CMD,
        "-y",
        "-i", str(input_path),
        "-vf", drawtext,
        "-c:a", "copy",  # copy audio
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        str(output_path)
    ]

    return await run_cmd(cmd)

async def process_url(url: str, sem: asyncio.Semaphore, watermark_text: str):
    async with sem:
        # download to temp dir
        tmp_base = TEMP_DIR
        tmp_base.mkdir(parents=True, exist_ok=True)

        ytdlp_cmd = [
            YT_DLP_CMD,
            "-f", FORMAT,
            "-o", str(tmp_base / YT_DLP_OUT_TEMPLATE),
            *EXTRA_OPTS,
            url
        ]
        print(f"[DOWN] {url}")
        rc, out = await run_cmd(ytdlp_cmd)
        if rc != 0:
            return False, f"yt-dlp failed (rc={rc})\n{out}"

        # find the downloaded file (we expect one new file under tmp_base)
        # Simple heuristic: find most-recent file under tmp_base
        files = list(tmp_base.rglob("*"))
        if not files:
            return False, "No file downloaded."
        # prefer files with video extensions
        video_files = [f for f in files if f.is_file() and f.suffix.lower() in (".mp4", ".m4v", ".webm", ".mov", ".flv", ".ts", ".mkv")]
        candidates = video_files if video_files else [f for f in files if f.is_file()]
        if not candidates:
            return False, "Downloaded item not found."

        # pick most recent
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        downloaded = candidates[0]

        # build final path based on uploader/id pattern used earlier
        # yt-dlp wrote to tmp_base/<uploader>/<id>.<ext>
        # We'll try to reconstruct uploader/id from path parts (best-effort)
        try:
            rel = downloaded.relative_to(tmp_base)
            parts = rel.parts
            if len(parts) >= 2:
                uploader = parts[0]
                filename = parts[-1]
                id_noext = Path(filename).stem
                final_out = FINAL_OUT_BASE / uploader / f"{id_noext}.mp4"
            else:
                final_out = FINAL_OUT_BASE / downloaded.name
        except Exception:
            final_out = FINAL_OUT_BASE / downloaded.name

        # choose font
        fontfile = find_font_path()
        rc2, out2 = await add_watermark(downloaded, final_out, watermark_text, fontfile=fontfile)
        if rc2 != 0:
            return False, f"ffmpeg failed (rc={rc2})\n{out2}"

        # optionally remove original downloaded file to save space
        try:
            downloaded.unlink()
        except Exception:
            pass

        print(f"[OK] {url} -> {final_out}")
        return True, str(final_out)

async def worker_with_retries(url: str, sem: asyncio.Semaphore, watermark_text: str):
    attempt = 1
    while attempt <= RETRIES:
        ok, info = await process_url(url, sem, watermark_text)
        if ok:
            return True, info
        else:
            print(f"[Attempt {attempt}] Failed for {url}: {info}")
            attempt += 1
            await asyncio.sleep(1 + attempt)
            
    return False, info

async def main_async(urls, watermark_text):
    sem = asyncio.Semaphore(CONCURRENT)
    tasks = [asyncio.create_task(worker_with_retries(u, sem, watermark_text)) for u in urls]
    results = await asyncio.gather(*tasks)
    success = sum(1 for r in results if r[0])
    print(f"Finished. Success {success}/{len(results)}")
    # log failures
    fails = [r for r in results if not r[0]]
    if fails:
        fail_log = OUTPUT_DIR / "failed_watermark.log"
        fail_log.parent.mkdir(parents=True, exist_ok=True)
        with fail_log.open("w", encoding="utf-8") as f:
            for ok, info in fails:
                f.write(info + "\n---\n")
        print(f"Some downloads failed; details in {fail_log}")

def read_urls(file: Path):
    if not file.exists():
        print(f"URLs file not found: {file}")
        return []
    return [line.strip() for line in file.read_text(encoding="utf-8").splitlines() if line.strip()]

def parse_args():
    p = argparse.ArgumentParser(description="Mass TikTok downloader + left-side text watermark")
    p.add_argument("--watermark", "-w", required=True, help="Teks watermark (contoh: 'Nama Saya')")
    p.add_argument("--urls", default=str(URLS_FILE), help="File berisi daftar URL (satu per baris)")
    p.add_argument("--concurrent", "-c", type=int, default=CONCURRENT, help="Jumlah download paralel")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    CONCURRENT = args.concurrent
    URLS_FILE = Path(args.urls)
    urls = read_urls(URLS_FILE)
    if not urls:
        print("Tidak ada URL ditemukan. Isi file URLs terlebih dahulu.")
        sys.exit(1)

    # check tools
    if shutil.which(YT_DLP_CMD) is None and YT_DLP_CMD == "yt-dlp":
        # attempt to continue; user may have installed in virtualenv
        pass
    if shutil.which(FFMPEG_CMD) is None and FFMPEG_CMD == "ffmpeg":
        print("ffmpeg tidak ditemukan di PATH. Silakan instal ffmpeg dan jalankan lagi.")
        sys.exit(1)

    # run
    asyncio.run(main_async(urls, args.watermark))
