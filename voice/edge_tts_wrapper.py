"""Wrapper for edge-tts text-to-speech."""
import asyncio
import edge_tts
from pathlib import Path
from typing import Optional, List
from utils.config import Config
from utils.logging_config import logger
from voice.voice_profiles import get_voice_for_recipe


async def list_voices() -> List[dict]:
    """List all available edge-tts voices."""
    voices = await edge_tts.list_voices()
    return voices


async def generate_speech(
    text: str,
    voice: str,
    output_path: Optional[Path] = None,
    rate: str = "+0%",
    pitch: str = "+0Hz",
    volume: str = "+0%"
) -> Path:
    """
    Generate speech from text using edge-tts.
    
    Args:
        text: Text to convert to speech
        voice: Voice name (e.g., "en-US-JennyNeural")
        output_path: Output file path (default: temp directory)
        rate: Speech rate adjustment (e.g., "+20%", "-10%")
        pitch: Pitch adjustment (e.g., "+10Hz", "-5Hz")
        volume: Volume adjustment (e.g., "+10%", "-5%")
        
    Returns:
        Path to generated audio file
    """
    if output_path is None:
        output_path = Config.TEMP_PATH / f"tts_{hash(text)}_{voice}.mp3"
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume
        )
        
        await communicate.save(str(output_path))
        logger.info(f"Generated TTS audio: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        raise


def generate_speech_sync(
    text: str,
    voice: str,
    output_path: Optional[Path] = None,
    rate: str = "+0%",
    pitch: str = "+0Hz",
    volume: str = "+0%"
) -> Path:
    """
    Synchronous wrapper for generate_speech.
    
    Args:
        text: Text to convert to speech
        voice: Voice name
        output_path: Output file path
        rate: Speech rate adjustment
        pitch: Pitch adjustment
        volume: Volume adjustment
        
    Returns:
        Path to generated audio file
    """
    return asyncio.run(
        generate_speech(text, voice, output_path, rate, pitch, volume)
    )


def generate_speech_for_recipe(
    text: str,
    recipe_name: str,
    output_path: Optional[Path] = None,
    voice_index: int = 0
) -> Path:
    """
    Generate speech using recipe-appropriate voice.
    
    Args:
        text: Text to convert to speech
        recipe_name: Recipe name (e.g., "brainrot", "news")
        output_path: Output file path
        voice_index: Voice index for recipe type
        
    Returns:
        Path to generated audio file
    """
    voice = get_voice_for_recipe(recipe_name, voice_index)
    logger.info(f"Using voice '{voice}' for recipe '{recipe_name}'")
    return generate_speech_sync(text, voice, output_path)


async def get_voice_metadata(voice: str) -> dict:
    """
    Get metadata for a specific voice.
    
    Args:
        voice: Voice name
        
    Returns:
        Voice metadata dictionary
    """
    voices = await list_voices()
    for v in voices:
        if v["Name"] == voice:
            return v
    raise ValueError(f"Voice '{voice}' not found")
