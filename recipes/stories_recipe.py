"""Stories recipe - vertical story format."""
from recipes.base_recipe import (
    RecipeBase, LayoutConfig, PacingConfig, AudioProfile, SubtitleStyle
)


class StoriesRecipe(RecipeBase):
    """Vertical story-style video format (9:16 aspect ratio)."""
    
    def get_name(self) -> str:
        return "stories"
    
    def get_default_duration(self) -> float:
        return 30.0  # Short stories, 30 seconds
    
    def get_default_resolution(self) -> str:
        return "vertical"  # 9:16 aspect ratio
    
    def get_default_fps(self) -> int:
        return 30
    
    def get_aspect_ratio(self) -> str:
        return "9:16"
    
    def generate_layout(self) -> LayoutConfig:
        return LayoutConfig(
            style="fullscreen",
            transition_type="fade",
            transition_duration=0.3
        )
    
    def get_pacing(self) -> PacingConfig:
        return PacingConfig(
            clip_duration_range=(3.0, 5.0),  # Medium-paced clips
            cut_speed="medium",
            fade_duration=0.3
        )
    
    def get_audio_profile(self) -> AudioProfile:
        return AudioProfile(
            voice_style="friendly",
            background_music=True,
            music_volume=0.4,  # Lower volume to not overpower narration
            sound_effects=False,
            narration_volume=0.85
        )
    
    def get_subtitle_style(self) -> SubtitleStyle:
        return SubtitleStyle(
            font="Arial",
            font_size=42,
            color="#FFFFFF",
            outline_color="#000000",
            position="center",
            animation="fade-in",
            bold=False
        )
    
    def get_story_prompt(self, topic: str) -> str:
        """Generate story-style script prompt."""
        return f"Write a short, engaging story script about: {topic}. Keep it conversational and friendly, suitable for a 30-second video."
