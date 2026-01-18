"""Voice profiles for different recipe types."""
from typing import Dict, List


# Voice mapping for edge-tts
# Format: {voice_style: [list of voice names]}
VOICE_PROFILES: Dict[str, List[str]] = {
    "energetic": [
        "en-US-JennyNeural",  # Energetic female
        "en-US-GuyNeural",    # Energetic male
        "en-US-AriaNeural",   # Expressive female
    ],
    "calm": [
        "en-US-MichelleNeural",  # Calm female
        "en-US-DavisNeural",     # Calm male
        "en-US-ChristopherNeural", # Gentle male
    ],
    "news": [
        "en-US-AriaNeural",      # Professional female
        "en-US-GuyNeural",       # Professional male
        "en-US-JennyNeural",     # Clear female
    ],
    "friendly": [
        "en-US-JennyNeural",     # Friendly female
        "en-US-MichelleNeural",  # Warm female
        "en-US-DavisNeural",     # Friendly male
    ],
}

# Recipe to voice style mapping
RECIPE_VOICE_MAP: Dict[str, str] = {
    "brainrot": "energetic",
    "news": "news",
    "stories": "friendly",
    "ambient": "calm",
    "loop10h": "calm",
}


def get_voice_for_recipe(recipe_name: str, voice_index: int = 0) -> str:
    """
    Get voice name for a recipe type.
    
    Args:
        recipe_name: Recipe name (e.g., "brainrot", "news")
        voice_index: Index in the voice list (default: 0)
        
    Returns:
        Voice name string
    """
    voice_style = RECIPE_VOICE_MAP.get(recipe_name, "friendly")
    voices = VOICE_PROFILES.get(voice_style, VOICE_PROFILES["friendly"])
    
    # Wrap around if index is out of range
    index = voice_index % len(voices)
    return voices[index]


def list_available_voices() -> Dict[str, List[str]]:
    """List all available voice profiles."""
    return VOICE_PROFILES.copy()
