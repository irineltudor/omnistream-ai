"""Interface for faster-whisper caption generation."""
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from faster_whisper import WhisperModel
from utils.config import Config
from utils.logging_config import logger


class CaptionWord:
    """Represents a single word with timing information."""
    
    def __init__(self, word: str, start: float, end: float, probability: float = 1.0):
        self.word = word
        self.start = start
        self.end = end
        self.probability = probability
    
    def __repr__(self):
        return f"CaptionWord('{self.word}', {self.start:.2f}-{self.end:.2f})"


class CaptionSegment:
    """Represents a caption segment with multiple words."""
    
    def __init__(self, words: List[CaptionWord], text: str, start: float, end: float):
        self.words = words
        self.text = text
        self.start = start
        self.end = end
    
    def __repr__(self):
        return f"CaptionSegment('{self.text}', {self.start:.2f}-{self.end:.2f})"


class WhisperInterface:
    """Interface for faster-whisper transcription."""
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Initialize Whisper model.
        
        Args:
            model_size: Model size ("tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3")
            device: Device to use ("cpu", "cuda")
            compute_type: Compute type ("int8", "int8_float16", "float16", "float32")
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model: Optional[WhisperModel] = None
        logger.info(f"Initializing Whisper model: {model_size} on {device}")
    
    def _load_model(self):
        """Lazy load the Whisper model."""
        if self.model is None:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("Whisper model loaded successfully")
    
    def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        word_timestamps: bool = True,
        beam_size: int = 5,
        best_of: int = 5,
        temperature: float = 0.0
    ) -> List[CaptionSegment]:
        """
        Transcribe audio file and return word-level timestamps.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., "en") or None for auto-detect
            word_timestamps: Whether to include word-level timestamps
            beam_size: Beam size for beam search
            best_of: Number of candidates for beam search
            temperature: Temperature for sampling
            
        Returns:
            List of CaptionSegment objects with word-level timestamps
        """
        self._load_model()
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Transcribing audio: {audio_path}")
        
        segments, info = self.model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=word_timestamps,
            beam_size=beam_size,
            best_of=best_of,
            temperature=temperature
        )
        
        logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
        
        caption_segments = []
        for segment in segments:
            words = []
            if hasattr(segment, 'words') and segment.words:
                for word_info in segment.words:
                    word = CaptionWord(
                        word=word_info.word,
                        start=word_info.start,
                        end=word_info.end,
                        probability=getattr(word_info, 'probability', 1.0)
                    )
                    words.append(word)
            
            caption_segment = CaptionSegment(
                words=words,
                text=segment.text.strip(),
                start=segment.start,
                end=segment.end
            )
            caption_segments.append(caption_segment)
        
        logger.info(f"Transcribed {len(caption_segments)} segments")
        return caption_segments
    
    def transcribe_to_srt(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        language: Optional[str] = None
    ) -> Path:
        """
        Transcribe audio and save as SRT subtitle file.
        
        Args:
            audio_path: Path to audio file
            output_path: Output SRT file path (default: same as audio with .srt extension)
            language: Language code or None for auto-detect
            
        Returns:
            Path to generated SRT file
        """
        if output_path is None:
            output_path = audio_path.with_suffix('.srt')
        
        segments = self.transcribe(audio_path, language=language)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start_time = self._format_timestamp(segment.start)
                end_time = self._format_timestamp(segment.end)
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment.text}\n\n")
        
        logger.info(f"Saved SRT file: {output_path}")
        return output_path
    
    def transcribe_to_vtt(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        language: Optional[str] = None
    ) -> Path:
        """
        Transcribe audio and save as VTT subtitle file.
        
        Args:
            audio_path: Path to audio file
            output_path: Output VTT file path (default: same as audio with .vtt extension)
            language: Language code or None for auto-detect
            
        Returns:
            Path to generated VTT file
        """
        if output_path is None:
            output_path = audio_path.with_suffix('.vtt')
        
        segments = self.transcribe(audio_path, language=language)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in segments:
                start_time = self._format_timestamp_vtt(segment.start)
                end_time = self._format_timestamp_vtt(segment.end)
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment.text}\n\n")
        
        logger.info(f"Saved VTT file: {output_path}")
        return output_path
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format timestamp for SRT format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    @staticmethod
    def _format_timestamp_vtt(seconds: float) -> str:
        """Format timestamp for VTT format (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


# Global whisper instance (lazy loaded)
_whisper_instance: Optional[WhisperInterface] = None


def get_whisper_instance(
    model_size: str = "base",
    device: str = "cpu",
    compute_type: str = "int8"
) -> WhisperInterface:
    """Get or create global Whisper instance."""
    global _whisper_instance
    if _whisper_instance is None:
        _whisper_instance = WhisperInterface(model_size, device, compute_type)
    return _whisper_instance
