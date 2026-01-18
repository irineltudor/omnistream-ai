# Universal Video Factory

Automated video generation system using 100% free/local tools. Generate multiple video formats (Brainrot, News, Stories, Ambient, and 10-Hour Loops) from a simple topic input.

## Features

- **Automated Video Generation**: Create videos from text topics using AI-powered recipe selection
- **Multiple Recipe Types**: 
  - Brainrot: Fast-paced, chaotic videos
  - News: Structured news-style format
  - Stories: Vertical 9:16 format for social media
  - Ambient: Slow, calming visuals
  - Loop10h: 10-hour looping ambient videos
- **Free Tools Only**: Uses edge-tts, faster-whisper, MoviePy, FFmpeg, and Pexels API
- **AI Director**: Gemini 2.5 Flash API for intelligent recipe selection
- **Word-by-Word Captions**: Stylized captions with word-level timing
- **Automated Upload**: Playwright scripts for multi-platform uploading

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd omnistream-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg (required for video processing):
- Windows: Download from https://ffmpeg.org/download.html
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

4. Install Playwright browsers (for automation):
```bash
playwright install chromium
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - GEMINI_API_KEY (for AI recipe selection)
# - PEXELS_API_KEY (for stock video/images)
```

## Usage

### Start the API Server

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### Generate a Video

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "serene forest ambience",
    "recipe": "auto",
    "duration": 60,
    "resolution": "1080p"
  }'
```

Response:
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "estimated_time": 120,
  "message": "Video generation started"
}
```

### Check Job Status

```bash
curl "http://localhost:8000/api/status/{job_id}"
```

### Download Video

```bash
curl "http://localhost:8000/api/download/{job_id}" --output video.mp4
```

## API Endpoints

- `POST /api/generate` - Start video generation
- `GET /api/status/{job_id}` - Check job status
- `GET /api/download/{job_id}` - Download completed video
- `GET /health` - Health check

## Project Structure

```
universal_video_factory/
├── api/                 # FastAPI endpoints
├── recipes/             # Video recipe classes
├── director/            # AI recipe selector
├── processor/           # Video rendering and processing
├── voice/               # TTS integration
├── subtitles/           # Caption generation
├── assets/              # Asset fetching (Pexels + local)
├── automation/          # Playwright upload scripts
└── utils/               # Configuration and helpers
```

## Configuration

Edit `.env` file to configure:
- API keys (Gemini, Pexels)
- Paths (assets, output, temp)
- Video settings (resolution, FPS, concurrent jobs)

## Local Assets

Place local assets in:
- `assets/local_clips/` - Video files (.mp4, .mov, .avi, .mkv)
- `assets/local_images/` - Image files (.jpg, .png, .webp)
- `assets/local_audio/` - Audio files (.mp3, .wav, .ogg)

## Automation

Use Playwright scripts for automated uploading:
- `automation/upload_template.py` - Multi-platform uploader
- `automation/gmail_verify.py` - Gmail verification code reader

## License

This project uses free/open-source tools. Please ensure compliance with:
- Pexels API terms (attribution required)
- edge-tts terms (check commercial use)
- All other tools are open-source

## Contributing

Contributions welcome! Please ensure all tools remain free/local.

## Notes

- Video generation is CPU/GPU intensive
- Large videos (10-hour loops) require significant disk space
- First run will download Whisper models (can be large)
- Ensure sufficient RAM for video processing
