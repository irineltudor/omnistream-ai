"""Example script to test video generation."""
import asyncio
from pathlib import Path
from recipes.recipe_manager import recipe_manager
from director.selector import get_director_selector
from voice.edge_tts_wrapper import generate_speech_for_recipe
from processor.renderer import VideoRenderer
from utils.config import Config
from utils.logging_config import logger


async def test_recipe_selection():
    """Test recipe selection."""
    print("Testing recipe selection...")
    director = get_director_selector()
    
    topics = [
        "serene forest ambience",
        "breaking news about AI",
        "funny story about cats",
        "chaotic meme compilation"
    ]
    
    for topic in topics:
        result = director.select_recipe(topic)
        print(f"Topic: {topic}")
        print(f"  Selected: {result['recipe']}")
        print(f"  Reasoning: {result['reasoning']}")
        print()


async def test_tts():
    """Test TTS generation."""
    print("Testing TTS generation...")
    test_text = "This is a test of the text to speech system."
    
    try:
        audio_path = generate_speech_for_recipe(
            test_text,
            "ambient",
            Config.TEMP_PATH / "test_tts.mp3"
        )
        print(f"Generated audio: {audio_path}")
        print(f"File exists: {audio_path.exists()}")
    except Exception as e:
        print(f"TTS test failed: {e}")


def test_recipe_manager():
    """Test recipe manager."""
    print("Testing recipe manager...")
    
    print("Available recipes:", recipe_manager.list_recipes())
    
    for recipe_name in recipe_manager.list_recipes():
        recipe = recipe_manager.get_recipe(recipe_name)
        print(f"\nRecipe: {recipe_name}")
        print(f"  Duration: {recipe.get_default_duration()}s")
        print(f"  Resolution: {recipe.get_default_resolution()}")
        print(f"  FPS: {recipe.get_default_fps()}")
        print(f"  Aspect Ratio: {recipe.get_aspect_ratio()}")


if __name__ == "__main__":
    print("Universal Video Factory - Test Script\n")
    print("=" * 50)
    
    # Test recipe manager
    test_recipe_manager()
    
    print("\n" + "=" * 50)
    
    # Test recipe selection
    asyncio.run(test_recipe_selection())
    
    print("=" * 50)
    
    # Test TTS
    asyncio.run(test_tts())
    
    print("\nTests completed!")
