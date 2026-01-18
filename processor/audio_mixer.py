"""Audio mixing module for combining TTS with background music."""
from pathlib import Path
from typing import Optional, List
from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips
from utils.config import Config
from utils.logging_config import logger


class AudioMixer:
    """Mixes TTS narration with background music and effects."""
    
    def __init__(self):
        """Initialize audio mixer."""
        self.temp_dir = Config.TEMP_PATH / "audio"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def mix_audio(
        self,
        narration_path: Path,
        background_music_path: Optional[Path] = None,
        music_volume: float = 0.5,
        narration_volume: float = 1.0,
        duration: Optional[float] = None,
        fade_in: float = 0.5,
        fade_out: float = 0.5,
        duck_narration: bool = False,
        duck_threshold: float = -20.0
    ) -> Path:
        """
        Mix narration with background music.
        
        Args:
            narration_path: Path to narration audio file
            background_music_path: Path to background music file (optional)
            music_volume: Volume of background music (0.0 to 1.0)
            narration_volume: Volume of narration (0.0 to 1.0)
            duration: Target duration in seconds (None uses narration duration)
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            duck_narration: Whether to duck music when narration plays
            duck_threshold: Threshold for ducking in dB
            
        Returns:
            Path to mixed audio file
        """
        logger.info(f"Mixing audio: narration={narration_path}, music={background_music_path}")
        
        # Load narration
        narration = AudioFileClip(str(narration_path))
        narration = narration.volumex(narration_volume)
        
        target_duration = duration or narration.duration
        
        # Load and prepare background music
        audio_clips = []
        if background_music_path and background_music_path.exists():
            music = AudioFileClip(str(background_music_path))
            music = music.volumex(music_volume)
            
            # Loop music to match duration if needed
            if music.duration < target_duration:
                loops_needed = int(target_duration / music.duration) + 1
                music_clips = [music] * loops_needed
                music = concatenate_audioclips(music_clips)
            
            # Trim to target duration
            music = music.subclip(0, target_duration)
            
            # Apply fade in/out
            if fade_in > 0:
                music = music.fadein(fade_in)
            if fade_out > 0:
                music = music.fadeout(fade_out)
            
            # Duck music if narration is present and ducking enabled
            if duck_narration:
                music = self._duck_audio(music, narration, duck_threshold)
            
            audio_clips.append(music)
        
        # Add narration
        if narration.duration < target_duration:
            # Extend narration with silence if needed
            from moviepy.audio.AudioClip import AudioArrayClip
            import numpy as np
            silence_duration = target_duration - narration.duration
            sample_rate = narration.fps
            silence = AudioArrayClip(
                np.zeros((int(silence_duration * sample_rate), 1)),
                fps=sample_rate
            )
            narration = concatenate_audioclips([narration, silence])
        else:
            narration = narration.subclip(0, target_duration)
        
        audio_clips.append(narration)
        
        # Composite audio
        if len(audio_clips) > 1:
            final_audio = CompositeAudioClip(audio_clips)
        else:
            final_audio = audio_clips[0]
        
        # Normalize audio
        final_audio = self._normalize_audio(final_audio)
        
        # Save mixed audio
        output_path = self.temp_dir / f"mixed_{hash(str(narration_path))}.mp3"
        final_audio.write_audiofile(
            str(output_path),
            codec='mp3',
            bitrate='192k',
            logger=None  # Suppress MoviePy logging
        )
        
        # Cleanup
        narration.close()
        if background_music_path:
            music.close()
        final_audio.close()
        
        logger.info(f"Mixed audio saved: {output_path}")
        return output_path
    
    def _duck_audio(
        self,
        music: AudioFileClip,
        narration: AudioFileClip,
        threshold: float = -20.0
    ) -> AudioFileClip:
        """
        Duck background music when narration is playing.
        
        Args:
            music: Background music clip
            narration: Narration clip
            threshold: Threshold in dB for ducking
            
        Returns:
            Duck-processed music clip
        """
        # Simple implementation: reduce music volume when narration is present
        # More sophisticated ducking would require audio analysis
        duck_factor = 0.3  # Reduce to 30% volume when ducking
        
        def make_frame(t):
            # Check if narration is active at this time
            if 0 <= t < narration.duration:
                # Duck the music
                return music.get_frame(t) * duck_factor
            else:
                return music.get_frame(t)
        
        return music.fl(make_frame, apply_to=['audio'])
    
    def _normalize_audio(self, audio: AudioFileClip) -> AudioFileClip:
        """
        Normalize audio levels.
        
        Args:
            audio: Audio clip to normalize
            
        Returns:
            Normalized audio clip
        """
        # Simple normalization: ensure peak doesn't exceed 0dB
        # More sophisticated normalization would analyze RMS levels
        max_volume = audio.max_volume()
        if max_volume > 0:
            # Normalize to 90% of max to avoid clipping
            target_volume = 0.9 / max_volume
            audio = audio.volumex(target_volume)
        
        return audio
    
    def concatenate_audio_files(
        self,
        audio_paths: List[Path],
        output_path: Optional[Path] = None,
        crossfade: float = 0.0
    ) -> Path:
        """
        Concatenate multiple audio files.
        
        Args:
            audio_paths: List of audio file paths
            output_path: Output file path (default: auto-generated)
            crossfade: Crossfade duration in seconds
            
        Returns:
            Path to concatenated audio file
        """
        if output_path is None:
            output_path = self.temp_dir / f"concatenated_{hash(str(audio_paths))}.mp3"
        
        clips = [AudioFileClip(str(path)) for path in audio_paths]
        
        if crossfade > 0:
            # Apply crossfades between clips
            for i in range(len(clips) - 1):
                clips[i] = clips[i].fadeout(crossfade)
                clips[i + 1] = clips[i + 1].fadein(crossfade)
        
        final_audio = concatenate_audioclips(clips)
        final_audio.write_audiofile(
            str(output_path),
            codec='mp3',
            bitrate='192k',
            logger=None
        )
        
        # Cleanup
        for clip in clips:
            clip.close()
        final_audio.close()
        
        logger.info(f"Concatenated {len(audio_paths)} audio files: {output_path}")
        return output_path


# Global audio mixer instance
_audio_mixer: Optional[AudioMixer] = None


def get_audio_mixer() -> AudioMixer:
    """Get or create global audio mixer instance."""
    global _audio_mixer
    if _audio_mixer is None:
        _audio_mixer = AudioMixer()
    return _audio_mixer
