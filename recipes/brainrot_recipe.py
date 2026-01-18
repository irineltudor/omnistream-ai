"""Brainrot recipe - fast cuts, chaotic visuals."""
from typing import List
from recipes.base_recipe import (
    RecipeBase, LayoutConfig, PacingConfig, AudioProfile, SubtitleStyle
)


class BrainrotRecipe(RecipeBase):
    """Fast-paced, chaotic video style with intense visuals."""
    
    def get_name(self) -> str:
        return "brainrot"
    
    def get_default_duration(self) -> float:
        return 60.0  # 1 minute default
    
    def get_default_resolution(self) -> str:
        return "1080p"
    
    def get_default_fps(self) -> int:
        return 60  # Higher FPS for smooth fast cuts
    
    def get_aspect_ratio(self) -> str:
        return "16:9"
    
    def generate_layout(self) -> LayoutConfig:
        return LayoutConfig(
            style="split-screen",
            transition_type="cut",
            transition_duration=0.1  # Very fast cuts
        )
    
    def get_pacing(self) -> PacingConfig:
        return PacingConfig(
            clip_duration_range=(1.0, 3.0),  # Very short clips
            cut_speed="fast",
            fade_duration=0.1
        )
    
    def get_audio_profile(self) -> AudioProfile:
        return AudioProfile(
            voice_style="energetic",
            background_music=True,
            music_volume=0.6,
            sound_effects=True,
            narration_volume=0.8
        )
    
    def get_subtitle_style(self) -> SubtitleStyle:
        return SubtitleStyle(
            font="Arial-Bold",
            font_size=48,
            color="#FFFFFF",
            outline_color="#000000",
            position="center",
            animation="word-by-word",
            bold=True
        )
    
    def get_keywords(self, topic: str) -> List[str]:
        """Generate intense, energetic keywords."""
        base_keywords = super().get_keywords(topic)
        # Add intensity modifiers
        intensity_words = ["intense", "fast", "chaotic", "energetic", "dynamic"]
        return base_keywords + intensity_words
