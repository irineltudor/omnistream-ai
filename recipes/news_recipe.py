"""News recipe - structured news format."""
from recipes.base_recipe import (
    RecipeBase, LayoutConfig, PacingConfig, AudioProfile, SubtitleStyle
)


class NewsRecipe(RecipeBase):
    """Structured news-style video format."""
    
    def get_name(self) -> str:
        return "news"
    
    def get_default_duration(self) -> float:
        return 120.0  # 2 minutes default
    
    def get_default_resolution(self) -> str:
        return "1080p"
    
    def get_default_fps(self) -> int:
        return 30
    
    def get_aspect_ratio(self) -> str:
        return "16:9"
    
    def generate_layout(self) -> LayoutConfig:
        return LayoutConfig(
            style="overlay",  # Lower thirds, title banners
            transition_type="fade",
            transition_duration=0.5
        )
    
    def get_pacing(self) -> PacingConfig:
        return PacingConfig(
            clip_duration_range=(5.0, 8.0),  # Longer clips for news
            cut_speed="medium",
            fade_duration=0.5
        )
    
    def get_audio_profile(self) -> AudioProfile:
        return AudioProfile(
            voice_style="news",
            background_music=False,  # News typically has minimal music
            music_volume=0.0,
            sound_effects=False,
            narration_volume=0.9  # Clear narration
        )
    
    def get_subtitle_style(self) -> SubtitleStyle:
        return SubtitleStyle(
            font="Arial",
            font_size=36,
            color="#FFFFFF",
            outline_color="#000000",
            position="bottom",
            animation="block",  # Block subtitles for readability
            bold=False
        )
    
    def get_story_prompt(self, topic: str) -> str:
        """Generate news-style script prompt."""
        return f"Write a professional news report script about: {topic}. Include an introduction, main points, and conclusion."
