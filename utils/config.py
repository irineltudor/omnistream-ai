"""Configuration management for Universal Video Factory."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    ASSETS_LOCAL_PATH: Path = BASE_DIR / os.getenv("ASSETS_LOCAL_PATH", "assets/local_clips")
    OUTPUT_PATH: Path = BASE_DIR / os.getenv("OUTPUT_PATH", "output")
    TEMP_PATH: Path = BASE_DIR / os.getenv("TEMP_PATH", "temp")
    
    # Video Settings
    DEFAULT_RESOLUTION: str = os.getenv("DEFAULT_RESOLUTION", "1080p")
    DEFAULT_FPS: int = int(os.getenv("DEFAULT_FPS", "30"))
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))
    
    # Resolution mappings
    RESOLUTION_MAP = {
        "1080p": (1920, 1080),
        "720p": (1280, 720),
        "vertical": (1080, 1920),  # 9:16 for stories
    }
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.ASSETS_LOCAL_PATH.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        cls.TEMP_PATH.mkdir(parents=True, exist_ok=True)
        (cls.BASE_DIR / "assets/local_images").mkdir(parents=True, exist_ok=True)
        (cls.BASE_DIR / "assets/local_audio").mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_resolution(cls, resolution: Optional[str] = None) -> tuple[int, int]:
        """Get resolution tuple from string."""
        res = resolution or cls.DEFAULT_RESOLUTION
        return cls.RESOLUTION_MAP.get(res, cls.RESOLUTION_MAP["1080p"])


# Initialize directories on import
Config.ensure_directories()
