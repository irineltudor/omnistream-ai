"""Ambient recipe - slow, calming visuals."""
from typing import List
from recipes.base_recipe import (
    RecipeBase, LayoutConfig, PacingConfig, AudioProfile, SubtitleStyle
)


class AmbientRecipe(RecipeBase):
    """Slow, calming ambient video style."""
    
    def get_name(self) -> str:
        return "ambient"
    
    def get_default_duration(self) -> float:
        return 300.0  # 5 minutes default
    
    def get_default_resolution(self) -> str:
        return "1080p"
    
    def get_default_fps(self) -> int:
        return 24  # Lower FPS for cinematic feel
    
    def get_aspect_ratio(self) -> str:
        return "16:9"
    
    def generate_layout(self) -> LayoutConfig:
        return LayoutConfig(
            style="ken-burns",  # Slow pan/zoom effects
            transition_type="crossfade",
            transition_duration=2.0  # Slow transitions
        )
    
    def get_pacing(self) -> PacingConfig:
        return PacingConfig(
            clip_duration_range=(30.0, 60.0),  # Very long clips
            cut_speed="slow",
            fade_duration=2.0
        )
    
    def get_audio_profile(self) -> AudioProfile:
        return AudioProfile(
            voice_style="calm",
            background_music=True,
            music_volume=0.7,  # Ambient music is prominent
            sound_effects=False,
            narration_volume=0.3  # Minimal or no narration
        )
    
    def get_subtitle_style(self) -> SubtitleStyle:
        return SubtitleStyle(
            font="Arial",
            font_size=32,
            color="#CCCCCC",  # Subtle color
            outline_color="#000000",
            position="bottom",
            animation="fade-in",
            bold=False
        )
    
    def get_keywords(self, topic: str) -> List[str]:
        """Generate calming, ambient keywords."""
        base_keywords = super().get_keywords(topic)
        ambient_words = ["calm", "peaceful", "serene", "ambient", "relaxing", "nature"]
        return base_keywords + ambient_words
    
    def get_story_prompt(self, topic: str) -> str:
        """Generate minimal script for ambient (mostly visual)."""
        return f"Create a brief, minimal description for an ambient video about: {topic}. Keep it very short, focusing on atmosphere."
