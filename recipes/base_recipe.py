"""Base recipe class for video generation."""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from utils.config import Config


@dataclass
class LayoutConfig:
    """Layout configuration for a recipe."""
    style: str  # "split-screen", "overlay", "fullscreen", "ken-burns"
    transition_type: str  # "cut", "fade", "wipe", "crossfade"
    transition_duration: float  # seconds


@dataclass
class PacingConfig:
    """Pacing configuration for a recipe."""
    clip_duration_range: Tuple[float, float]  # (min, max) seconds per clip
    cut_speed: str  # "fast", "medium", "slow"
    fade_duration: float  # seconds


@dataclass
class AudioProfile:
    """Audio profile configuration."""
    voice_style: str  # "energetic", "calm", "news", "friendly"
    background_music: bool
    music_volume: float  # 0.0 to 1.0
    sound_effects: bool
    narration_volume: float  # 0.0 to 1.0


@dataclass
class SubtitleStyle:
    """Subtitle styling configuration."""
    font: str
    font_size: int
    color: str  # hex color
    outline_color: str  # hex color
    position: str  # "bottom", "center", "top"
    animation: str  # "word-by-word", "block", "fade-in"
    bold: bool


class RecipeBase(ABC):
    """Abstract base class for video recipes."""
    
    def __init__(
        self,
        duration: Optional[float] = None,
        resolution: Optional[str] = None,
        fps: Optional[int] = None
    ):
        """
        Initialize recipe.
        
        Args:
            duration: Video duration in seconds (None uses recipe default)
            resolution: Video resolution (None uses recipe default)
            fps: Frames per second (None uses recipe default)
        """
        self.duration = duration or self.get_default_duration()
        self.resolution = resolution or self.get_default_resolution()
        self.fps = fps or self.get_default_fps()
        self.aspect_ratio = self.get_aspect_ratio()
    
    @abstractmethod
    def get_name(self) -> str:
        """Get recipe name."""
        pass
    
    @abstractmethod
    def get_default_duration(self) -> float:
        """Get default video duration in seconds."""
        pass
    
    @abstractmethod
    def get_default_resolution(self) -> str:
        """Get default resolution string."""
        pass
    
    @abstractmethod
    def get_default_fps(self) -> int:
        """Get default frames per second."""
        pass
    
    @abstractmethod
    def get_aspect_ratio(self) -> str:
        """Get aspect ratio (e.g., '16:9', '9:16', '1:1')."""
        pass
    
    @abstractmethod
    def generate_layout(self) -> LayoutConfig:
        """Generate layout configuration for this recipe."""
        pass
    
    @abstractmethod
    def get_pacing(self) -> PacingConfig:
        """Get pacing configuration for this recipe."""
        pass
    
    @abstractmethod
    def get_audio_profile(self) -> AudioProfile:
        """Get audio profile for this recipe."""
        pass
    
    @abstractmethod
    def get_subtitle_style(self) -> SubtitleStyle:
        """Get subtitle style configuration for this recipe."""
        pass
    
    def get_resolution_tuple(self) -> Tuple[int, int]:
        """Get resolution as (width, height) tuple."""
        return Config.get_resolution(self.resolution)
    
    def get_keywords(self, topic: str) -> List[str]:
        """
        Generate search keywords from topic.
        Can be overridden by subclasses for recipe-specific keyword generation.
        
        Args:
            topic: Input topic string
            
        Returns:
            List of keywords for asset search
        """
        # Default: split topic into words
        return [word.strip() for word in topic.lower().split() if len(word.strip()) > 2]
    
    def get_story_prompt(self, topic: str) -> str:
        """
        Generate story/script prompt for this recipe.
        Can be overridden by subclasses.
        
        Args:
            topic: Input topic string
            
        Returns:
            Prompt for story generation
        """
        return f"Create a {self.get_name()} style video script about: {topic}"
