# TikTok Video Downloader with Watermark

A powerful Python script for downloading TikTok videos in bulk and adding custom text watermarks using FFmpeg.

## Features

- ✅ **Bulk Download**: Download multiple TikTok videos from a list of URLs
- ✅ **High Quality**: Downloads videos in HD quality (1080p+ preferred)
- ✅ **Custom Watermarks**: Add custom text watermarks to videos
- ✅ **Parallel Processing**: Download multiple videos simultaneously
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux
- ✅ **Retry Logic**: Automatic retry on failed downloads
- ✅ **Progress Tracking**: Real-time progress updates

## Prerequisites

### Required Software
- **Python 3.7+**
- **FFmpeg** (for watermarking)
- **yt-dlp** (for downloading TikTok videos)

### Installation

#### 1. Install Python
Download and install Python from [python.org](https://www.python.org/downloads/)

#### 2. Install FFmpeg
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

#### 3. Install yt-dlp
```bash
pip install yt-dlp
```

#### 4. Clone or Download
```bash
git clone https://github.com/siyoell12/AUTO-DOWNLOAD-VIDEO-TIKTOK.git
cd AUTO-DOWNLOAD-VIDEO-TIKTOK
```

## Quick Start

### 1. Prepare URLs
Create a file named `urls.txt` with one TikTok URL per line:
```
https://www.tiktok.com/@username/video/1234567890
https://www.tiktok.com/@anotheruser/video/0987654321
```

### 2. Run the Script
```bash
# Basic usage
python dea.py -w "Your Watermark Text"

# With custom URLs file
python dea.py -w "Your Watermark" --urls my_urls.txt

# With custom concurrent downloads
python dea.py -w "Your Watermark" -c 5
```

## Usage Guide

### Command Line Arguments
| Argument | Description | Example |
|----------|-------------|---------|
| `-w, --watermark` | **Required** Watermark text to add | `-w "My Channel"` |
| `--urls` | Custom URLs file (default: urls.txt) | `--urls videos.txt` |
| `-c, --concurrent` | Number of parallel downloads (default: 3) | `-c 5` |

### Examples

#### Basic Usage
```bash
python dea.py -w "AIRDROP INDEPENDEN"
```

#### Advanced Usage
```bash
# Download with 5 concurrent processes
python dea.py -w "My Brand" -c 5

# Use custom URLs file
python dea.py -w "Copyright 2024" --urls custom_urls.txt
```

## Output Structure

```
downloads/
├── watermarked/
│   ├── username1/
│   │   ├── video1.mp4
│   │   └── video2.mp4
│   └── username2/
│       ├── video3.mp4
│       └── video4.mp4
├── failed_watermark.log  # Failed downloads log
└── ...
```

## Troubleshooting

### Common Issues

#### 1. FFmpeg Not Found
**Error**: `ffmpeg tidak ditemukan di PATH`
**Solution**: Install FFmpeg and add it to your system PATH

#### 2. Font Issues
**Error**: Font not found
**Solution**: The script will automatically try common fonts. On Windows, ensure Arial.ttf exists in C:\Windows\Fonts

#### 3. Download Failures
**Error**: yt-dlp failed
**Solution**: 
- Check your internet connection
- Ensure URLs are valid TikTok links
- Check `downloads/failed_watermark.log` for details

#### 4. Permission Errors
**Error**: Permission denied
**Solution**: Run terminal as administrator or check folder permissions

### Manual Testing
To test if FFmpeg is working correctly:
```bash
ffmpeg -version
```

To test if yt-dlp is working:
```bash
yt-dlp --version
```

## Configuration

### Default Settings
- **Concurrent Downloads**: 3
- **Retries**: 3 attempts
- **Output Format**: MP4
- **Video Quality**: 720p+ preferred
- **Watermark Position**: Left side, vertical center

### Customization
You can modify these settings in the script:
- `CONCURRENT`: Number of parallel downloads
- `RETRIES`: Number of retry attempts
- `FORMAT`: Video quality preference
- `fontsize`: Watermark font size
- `padding`: Watermark position from edge

## 🌐 Komunitas & Sosial Media

Ingin berdiskusi, bertanya, atau berbagi ide? Bergabunglah dengan komunitas kami!

💬 Telegram Group: [t.me/airdropindependen](https://t.me/independendropers)

🐦 Twitter/X: [twitter.com/deasaputra12](https://x.com/Deasaputra_12)

🎮 Discord Server: [discord.gg/airdropindependen](https://discord.gg/Tuy2bR6CkU)


## Buy Me a Coffee

- **EVM:** 0x905d0505Ec007C9aDb5CF005535bfcC5E43c0B66
- **TON:** UQCFO7vVP0N8_K4JUCfqlK6tsofOF4KEhpahEEdXBMQ-MVQL
- **SOL:** BmqfjRHAKXUSKATuhbjPZfcNciN3J2DA1tqMgw9aGMdj

Thank you for visiting this repository, don't forget to contribute in the form of follows and stars.
If you have questions, find an issue, or have suggestions for improvement, feel free to contact me or open an *issue* in this GitHub repository.

**deasaputra**
