"""Main video rendering engine using MoviePy."""
import random
from pathlib import Path
from typing import List, Optional
from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips,
    AudioFileClip
)
from PIL import Image
import numpy as np
from utils.config import Config
from utils.logging_config import logger
from utils.video_helpers import ken_burns_effect, fade_transition, crossfade, split_screen
from recipes.base_recipe import RecipeBase
from assets.fetcher import get_asset_fetcher
from processor.subtitle_engine import get_subtitle_engine
from processor.audio_mixer import get_audio_mixer


class VideoRenderer:
    """Main video rendering engine."""
    
    def __init__(self):
        """Initialize video renderer."""
        self.temp_dir = Config.TEMP_PATH / "render"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.asset_fetcher = get_asset_fetcher()
        self.subtitle_engine = get_subtitle_engine()
        self.audio_mixer = get_audio_mixer()
    
    def render_video(
        self,
        recipe: RecipeBase,
        topic: str,
        story_text: str,
        narration_audio: Path,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Render complete video from recipe and assets.
        
        Args:
            recipe: Recipe instance
            topic: Video topic
            story_text: Story/script text
            narration_audio: Path to narration audio file
            output_path: Output video path (default: auto-generated)
            
        Returns:
            Path to rendered video file
        """
        logger.info(f"Rendering video with recipe: {recipe.get_name()}")
        
        if output_path is None:
            output_path = Config.OUTPUT_PATH / f"video_{recipe.get_name()}_{hash(topic)}.mp4"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get recipe configuration
        layout = recipe.generate_layout()
        pacing = recipe.get_pacing()
        audio_profile = recipe.get_audio_profile()
        subtitle_style = recipe.get_subtitle_style()
        resolution = recipe.get_resolution_tuple()
        fps = recipe.fps
        
        # Fetch assets
        keywords = recipe.get_keywords(topic)
        logger.info(f"Fetching assets with keywords: {keywords}")
        
        video_clips_paths = self.asset_fetcher.fetch_videos(keywords, count=10)
        image_paths = self.asset_fetcher.fetch_images(keywords, count=10)
        
        # Prepare video clips
        video_clips = self._prepare_video_clips(
            video_clips_paths,
            image_paths,
            recipe,
            layout,
            pacing,
            resolution
        )
        
        # Combine video clips
        if len(video_clips) > 1:
            final_video = concatenate_videoclips(video_clips, method="compose")
        else:
            final_video = video_clips[0] if video_clips else self._create_placeholder_clip(recipe, resolution)
        
        # Trim to target duration
        target_duration = min(recipe.duration, final_video.duration)
        final_video = final_video.subclip(0, target_duration)
        
        # Add subtitles if narration exists
        if narration_audio.exists() and audio_profile.narration_volume > 0:
            subtitle_clips = self.subtitle_engine.render_subtitles(
                narration_audio,
                subtitle_style,
                final_video.duration,
                resolution
            )
            final_video = self.subtitle_engine.composite_subtitles(final_video, subtitle_clips)
        
        # Add audio
        if narration_audio.exists():
            # Mix audio with background music if needed
            background_music = None
            if audio_profile.background_music:
                music_paths = self.asset_fetcher._get_local_audio_files()
                if music_paths:
                    background_music = random.choice(music_paths)
                else:
                    # Try to find music in local audio directory
                    local_audio_path = Config.BASE_DIR / "assets" / "local_audio"
                    if local_audio_path.exists():
                        music_files = list(local_audio_path.glob("*.mp3"))
                        if music_files:
                            background_music = random.choice(music_files)
            
            mixed_audio_path = self.audio_mixer.mix_audio(
                narration_audio,
                background_music,
                music_volume=audio_profile.music_volume,
                narration_volume=audio_profile.narration_volume,
                duration=final_video.duration,
                fade_in=pacing.fade_duration,
                fade_out=pacing.fade_duration
            )
            
            audio_clip = AudioFileClip(str(mixed_audio_path))
            final_video = final_video.set_audio(audio_clip)
        
        # Set FPS and write video
        final_video = final_video.set_fps(fps)
        
        logger.info(f"Writing video to: {output_path}")
        final_video.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=fps,
            bitrate='8000k',
            logger=None  # Suppress MoviePy logging
        )
        
        # Cleanup
        final_video.close()
        if narration_audio.exists():
            audio_clip.close()
        
        logger.info(f"Video rendered successfully: {output_path}")
        return output_path
    
    def _prepare_video_clips(
        self,
        video_paths: List[Path],
        image_paths: List[Path],
        recipe: RecipeBase,
        layout,
        pacing,
        resolution: tuple[int, int]
    ) -> List[VideoFileClip]:
        """Prepare and process video clips according to recipe."""
        clips = []
        width, height = resolution
        
        # Determine clip duration range
        min_duration, max_duration = pacing.clip_duration_range
        
        # Process video clips
        for video_path in video_paths:
            if not video_path.exists():
                continue
            
            try:
                clip = VideoFileClip(str(video_path))
                clip = clip.resize(resolution)
                
                # Apply duration based on pacing
                target_duration = random.uniform(min_duration, max_duration)
                if clip.duration > target_duration:
                    # Random start point
                    start = random.uniform(0, max(0, clip.duration - target_duration))
                    clip = clip.subclip(start, start + target_duration)
                elif clip.duration < target_duration:
                    # Loop if too short
                    loops_needed = int(target_duration / clip.duration) + 1
                    clip = concatenate_videoclips([clip] * loops_needed).subclip(0, target_duration)
                
                # Apply transitions based on layout
                if layout.transition_type == "fade":
                    clip = fade_transition(clip, layout.transition_duration)
                elif layout.transition_type == "crossfade" and clips:
                    clip = crossfade(clips[-1], clip, layout.transition_duration)
                
                clips.append(clip)
                
            except Exception as e:
                logger.warning(f"Failed to process video {video_path}: {e}")
                continue
        
        # Process image clips (for ambient/Ken Burns style)
        if layout.style == "ken-burns" and image_paths:
            for image_path in image_paths[:5]:  # Limit images
                if not image_path.exists():
                    continue
                
                try:
                    img_clip = ImageClip(str(image_path))
                    img_clip = img_clip.resize(resolution)
                    
                    # Apply Ken Burns effect
                    duration = random.uniform(min_duration, max_duration)
                    img_clip = img_clip.set_duration(duration)
                    img_clip = ken_burns_effect(img_clip, duration=duration)
                    
                    clips.append(img_clip)
                    
                except Exception as e:
                    logger.warning(f"Failed to process image {image_path}: {e}")
                    continue
        
        # Apply layout styles
        if layout.style == "split-screen" and len(clips) >= 2:
            # Create split-screen effects
            split_clips = []
            for i in range(0, len(clips) - 1, 2):
                clip1 = clips[i]
                clip2 = clips[i + 1] if i + 1 < len(clips) else clips[i]
                split_clip = split_screen(clip1, clip2, position="horizontal")
                split_clips.append(split_clip)
            clips = split_clips
        
        return clips
    
    def _create_placeholder_clip(
        self,
        recipe: RecipeBase,
        resolution: tuple[int, int]
    ) -> VideoFileClip:
        """Create a placeholder video clip if no assets available."""
        width, height = resolution
        duration = min(recipe.duration, 10.0)  # Max 10 seconds placeholder
        
        # Create solid color frame
        color = (50, 50, 50)  # Dark gray
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = color
        
        # Create clip from frame
        from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
        clip = ImageSequenceClip([frame], fps=recipe.fps)
        clip = clip.set_duration(duration)
        
        logger.warning("No assets available, using placeholder clip")
        return clip


