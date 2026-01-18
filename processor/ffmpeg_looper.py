"""FFmpeg integration for creating long looping videos."""
import subprocess
from pathlib import Path
from typing import Optional
from utils.config import Config
from utils.logging_config import logger


class FFmpegLooper:
    """Creates long looping videos using FFmpeg."""
    
    def __init__(self):
        """Initialize FFmpeg looper."""
        self.temp_dir = Config.TEMP_PATH / "loops"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def create_loop(
        self,
        input_video: Path,
        output_path: Path,
        target_duration: float,
        seamless: bool = True
    ) -> Path:
        """
        Create a looping video of specified duration.
        
        Args:
            input_video: Input video file to loop
            output_path: Output video path
            target_duration: Target duration in seconds
            seamless: Whether to create seamless loop (fade in/out)
            
        Returns:
            Path to looped video file
        """
        logger.info(f"Creating {target_duration}s loop from {input_video}")
        
        if not input_video.exists():
            raise FileNotFoundError(f"Input video not found: {input_video}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if seamless:
            return self._create_seamless_loop(input_video, output_path, target_duration)
        else:
            return self._create_simple_loop(input_video, output_path, target_duration)
    
    def _create_simple_loop(
        self,
        input_video: Path,
        output_path: Path,
        target_duration: float
    ) -> Path:
        """
        Create simple loop using FFmpeg stream_loop.
        
        Args:
            input_video: Input video
            output_path: Output path
            target_duration: Target duration
            
        Returns:
            Output path
        """
        # Use FFmpeg's stream_loop to loop the video
        cmd = [
            "ffmpeg",
            "-stream_loop", "-1",  # Infinite loop
            "-i", str(input_video),
            "-t", str(target_duration),  # Duration limit
            "-c", "copy",  # Copy codec (fast)
            "-y",  # Overwrite output
            str(output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Created loop video: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise RuntimeError(f"Failed to create loop: {e.stderr}")
    
    def _create_seamless_loop(
        self,
        input_video: Path,
        output_path: Path,
        target_duration: float
    ) -> Path:
        """
        Create seamless loop with crossfade for smooth transitions.
        
        Args:
            input_video: Input video
            output_path: Output path
            target_duration: Target duration
            
        Returns:
            Output path
        """
        # For seamless loops, we need to:
        # 1. Create multiple copies of the video
        # 2. Apply crossfade between copies
        # 3. Concatenate them
        
        # First, get video duration
        duration = self._get_video_duration(input_video)
        if duration == 0:
            raise ValueError(f"Invalid video duration: {duration}")
        
        # Calculate how many loops we need
        loops_needed = int(target_duration / duration) + 2  # Extra for crossfade
        
        # Create looped video with crossfade
        # This is a simplified version - full seamless loop would require more complex processing
        temp_concat_file = self.temp_dir / "concat_list.txt"
        
        # Create concat file list
        with open(temp_concat_file, 'w') as f:
            for _ in range(loops_needed):
                f.write(f"file '{input_video.absolute()}'\n")
        
        # Use concat demuxer with crossfade filter
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(temp_concat_file),
            "-vf", "fade=t=in:st=0:d=1,fade=t=out:st={}:d=1".format(target_duration - 1),
            "-af", "afade=t=in:st=0:d=1,afade=t=out:st={}:d=1".format(target_duration - 1),
            "-t", str(target_duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            str(output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Created seamless loop video: {output_path}")
            
            # Cleanup
            if temp_concat_file.exists():
                temp_concat_file.unlink()
            
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            # Fallback to simple loop
            logger.warning("Falling back to simple loop")
            return self._create_simple_loop(input_video, output_path, target_duration)
    
    def _get_video_duration(self, video_path: Path) -> float:
        """
        Get video duration using FFprobe.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.warning(f"Failed to get video duration: {e}")
            return 0.0
    
    def loop_audio(
        self,
        input_audio: Path,
        output_path: Path,
        target_duration: float
    ) -> Path:
        """
        Loop audio file to target duration.
        
        Args:
            input_audio: Input audio file
            output_path: Output path
            target_duration: Target duration in seconds
            
        Returns:
            Output path
        """
        logger.info(f"Looping audio to {target_duration}s")
        
        cmd = [
            "ffmpeg",
            "-stream_loop", "-1",
            "-i", str(input_audio),
            "-t", str(target_duration),
            "-c", "copy",
            "-y",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Created looped audio: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise RuntimeError(f"Failed to loop audio: {e.stderr}")


# Global FFmpeg looper instance
_ffmpeg_looper: Optional[FFmpegLooper] = None


def get_ffmpeg_looper() -> FFmpegLooper:
    """Get or create global FFmpeg looper instance."""
    global _ffmpeg_looper
    if _ffmpeg_looper is None:
        _ffmpeg_looper = FFmpegLooper()
    return _ffmpeg_looper
