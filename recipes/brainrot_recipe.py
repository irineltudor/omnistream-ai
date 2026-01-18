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
            style="fullscreen",
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
        """Generate stock-footage-friendly keywords from topic."""
        # Map common topics to better stock footage search terms
        keyword_mappings = {
            "messi": ["soccer", "football", "athlete", "sports"],
            "ronaldo": ["soccer", "football", "athlete", "sports"],
            "football": ["soccer", "sports", "stadium", "athlete"],
            "soccer": ["football", "sports", "stadium", "goal"],
            "basketball": ["sports", "athlete", "basketball court", "slam dunk"],
            "gaming": ["gaming", "esports", "computer", "neon lights"],
            "backflip": ["gymnastics", "acrobatics", "parkour", "extreme sports"],
            "backflips": ["gymnastics", "acrobatics", "parkour", "extreme sports"],
            "car": ["car", "racing", "sports car", "speed"],
            "money": ["money", "cash", "success", "business"],
            "gym": ["gym", "fitness", "workout", "muscles"],
            "workout": ["fitness", "gym", "exercise", "training"],
        }
        
        # Extract base keywords from topic
        topic_lower = topic.lower()
        keywords = []
        
        # Check for mapped keywords
        for key, mapped_words in keyword_mappings.items():
            if key in topic_lower:
                keywords.extend(mapped_words)
        
        # If no mappings found, use the topic words directly
        if not keywords:
            keywords = [word.strip() for word in topic_lower.split() if len(word.strip()) > 2]
        
        # Add some generic energetic/brainrot style keywords
        style_keywords = ["action", "dynamic", "energy"]
        
        # Return unique keywords, prioritizing mapped ones
        seen = set()
        result = []
        for kw in keywords + style_keywords:
            if kw not in seen:
                seen.add(kw)
                result.append(kw)
        
        return result[:8]  # Limit to 8 keywords
