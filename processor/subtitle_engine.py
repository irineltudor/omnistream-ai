"""Subtitle engine for rendering word-by-word captions."""
from pathlib import Path
from typing import List, Optional
from moviepy.editor import VideoClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from utils.logging_config import logger
from subtitles.whisper_interface import WhisperInterface, CaptionWord, CaptionSegment
from recipes.base_recipe import SubtitleStyle


class SubtitleEngine:
    """Renders stylized subtitles with word-by-word animations."""
    
    def __init__(self, whisper_interface: Optional[WhisperInterface] = None):
        """
        Initialize subtitle engine.
        
        Args:
            whisper_interface: Whisper interface instance (creates new if None)
        """
        self.whisper = whisper_interface or WhisperInterface()
    
    def render_subtitles(
        self,
        audio_path: Path,
        subtitle_style: SubtitleStyle,
        video_duration: float,
        video_size: tuple[int, int],
        output_path: Optional[Path] = None
    ) -> List[VideoClip]:
        """
        Render subtitles as video clips.
        
        Args:
            audio_path: Path to audio file for transcription
            subtitle_style: Subtitle styling configuration
            video_duration: Total video duration
            video_size: Video size (width, height)
            output_path: Optional output path (not used, returns clips)
            
        Returns:
            List of TextClip objects for subtitles
        """
        logger.info(f"Rendering subtitles from audio: {audio_path}")
        
        # Transcribe audio
        segments = self.whisper.transcribe(audio_path)
        
        # Generate subtitle clips based on style
        if subtitle_style.animation == "word-by-word":
            return self._render_word_by_word(segments, subtitle_style, video_size)
        elif subtitle_style.animation == "block":
            return self._render_block_subtitles(segments, subtitle_style, video_size)
        else:  # fade-in
            return self._render_fade_in(segments, subtitle_style, video_size)
    
    def _render_word_by_word(
        self,
        segments: List[CaptionSegment],
        style: SubtitleStyle,
        video_size: tuple[int, int]
    ) -> List[VideoClip]:
        """Render word-by-word animated subtitles."""
        clips = []
        width, height = video_size
        
        for segment in segments:
            if not segment.words:
                # Fallback to block if no word timestamps
                word_clip = self._create_text_clip(
                    segment.text,
                    style,
                    video_size,
                    segment.start,
                    segment.end
                )
                clips.append(word_clip)
                continue
            
            # Render each word separately
            for i, word in enumerate(segment.words):
                word_clip = self._create_text_clip(
                    word.word,
                    style,
                    video_size,
                    word.start,
                    word.end
                )
                clips.append(word_clip)
        
        return clips
    
    def _render_block_subtitles(
        self,
        segments: List[CaptionSegment],
        style: SubtitleStyle,
        video_size: tuple[int, int]
    ) -> List[VideoClip]:
        """Render block subtitles (entire segments at once)."""
        clips = []
        
        for segment in segments:
            clip = self._create_text_clip(
                segment.text,
                style,
                video_size,
                segment.start,
                segment.end
            )
            clips.append(clip)
        
        return clips
    
    def _render_fade_in(
        self,
        segments: List[CaptionSegment],
        style: SubtitleStyle,
        video_size: tuple[int, int]
    ) -> List[VideoClip]:
        """Render subtitles with fade-in animation."""
        clips = []
        fade_duration = 0.3
        
        for segment in segments:
            clip = self._create_text_clip(
                segment.text,
                style,
                video_size,
                segment.start,
                segment.end
            )
            # Apply fade in/out
            clip = clip.fadein(fade_duration).fadeout(fade_duration)
            clips.append(clip)
        
        return clips
    
    def _create_text_clip(
        self,
        text: str,
        style: SubtitleStyle,
        video_size: tuple[int, int],
        start_time: float,
        end_time: float
    ) -> TextClip:
        """
        Create a styled text clip.
        
        Args:
            text: Text to display
            style: Subtitle style configuration
            video_size: Video size (width, height)
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            TextClip object
        """
        width, height = video_size
        
        # Calculate position
        if style.position == "bottom":
            position = ("center", height - style.font_size - 50)
        elif style.position == "top":
            position = ("center", 50)
        else:  # center
            position = ("center", "center")
        
        # Create text clip
        txt_clip = TextClip(
            text,
            fontsize=style.font_size,
            color=style.color,
            font=style.font.replace("-Bold", "") if "-Bold" in style.font else style.font,
            stroke_color=style.outline_color,
            stroke_width=2,
            method="caption",
            size=(width - 100, None),  # Leave margins
            align="center"
        )
        
        # Set timing and position
        txt_clip = txt_clip.set_start(start_time).set_duration(end_time - start_time)
        txt_clip = txt_clip.set_position(position)
        
        return txt_clip
    
    def composite_subtitles(
        self,
        video_clip: VideoClip,
        subtitle_clips: List[VideoClip]
    ) -> VideoClip:
        """
        Composite subtitles onto video.
        
        Args:
            video_clip: Base video clip
            subtitle_clips: List of subtitle clips
            
        Returns:
            Composite video clip with subtitles
        """
        if not subtitle_clips:
            return video_clip
        
        # Combine all subtitle clips
        all_clips = [video_clip] + subtitle_clips
        return CompositeVideoClip(all_clips)


# Global subtitle engine instance
_subtitle_engine: Optional[SubtitleEngine] = None


def get_subtitle_engine(whisper_interface: Optional[WhisperInterface] = None) -> SubtitleEngine:
    """Get or create global subtitle engine instance."""
    global _subtitle_engine
    if _subtitle_engine is None:
        _subtitle_engine = SubtitleEngine(whisper_interface)
    return _subtitle_engine
