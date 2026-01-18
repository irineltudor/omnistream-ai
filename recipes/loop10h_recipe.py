"""10-hour loop recipe - extends ambient for long looping videos."""
from recipes.ambient_recipe import AmbientRecipe
from recipes.base_recipe import LayoutConfig, PacingConfig


class Loop10hRecipe(AmbientRecipe):
    """10-hour looping ambient video."""
    
    def get_name(self) -> str:
        return "loop10h"
    
    def get_default_duration(self) -> float:
        return 36000.0  # 10 hours = 36000 seconds
    
    def generate_layout(self) -> LayoutConfig:
        # Same as ambient but optimized for looping
        return LayoutConfig(
            style="ken-burns",
            transition_type="crossfade",
            transition_duration=3.0  # Even slower for seamless loops
        )
    
    def get_pacing(self) -> PacingConfig:
        # Longer clips for seamless looping
        return PacingConfig(
            clip_duration_range=(60.0, 120.0),  # 1-2 minute clips
            cut_speed="slow",
            fade_duration=3.0
        )
    
    def get_story_prompt(self, topic: str) -> str:
        """Minimal script for looping ambient video."""
        return f"Create a very brief, atmospheric description for a 10-hour looping ambient video about: {topic}. Focus on visual elements that can loop seamlessly."
