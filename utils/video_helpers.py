"""Video helper functions for effects and transitions."""
from typing import Tuple
from moviepy.editor import VideoClip, ImageClip, CompositeVideoClip
import numpy as np


def ken_burns_effect(
    clip: ImageClip,
    start_scale: float = 1.0,
    end_scale: float = 1.2,
    start_pos: Tuple[float, float] = (0.5, 0.5),
    end_pos: Tuple[float, float] = (0.4, 0.4),
    duration: float = None
) -> VideoClip:
    """
    Apply Ken Burns effect (pan and zoom) to an image clip.
    
    Args:
        clip: ImageClip to apply effect to
        start_scale: Starting zoom scale (1.0 = no zoom)
        end_scale: Ending zoom scale
        start_pos: Starting position as (x, y) normalized coordinates (0-1)
        end_pos: Ending position as (x, y) normalized coordinates (0-1)
        duration: Duration of the effect (uses clip duration if None)
    
    Returns:
        VideoClip with Ken Burns effect applied
    """
    if duration is None:
        duration = clip.duration
    
    def make_frame(t):
        # Calculate progress (0 to 1)
        progress = t / duration if duration > 0 else 0
        progress = min(1.0, max(0.0, progress))
        
        # Interpolate scale and position
        scale = start_scale + (end_scale - start_scale) * progress
        x_pos = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
        y_pos = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
        
        # Get frame dimensions
        frame = clip.get_frame(0)
        h, w = frame.shape[:2]
        
        # Calculate crop size
        crop_w = int(w / scale)
        crop_h = int(h / scale)
        
        # Calculate crop position
        crop_x = int((w - crop_w) * x_pos)
        crop_y = int((h - crop_h) * y_pos)
        
        # Crop and resize
        cropped = frame[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]
        
        # Resize back to original dimensions
        from PIL import Image
        img = Image.fromarray(cropped)
        img_resized = img.resize((w, h), Image.Resampling.LANCZOS)
        
        return np.array(img_resized)
    
    return clip.fl(make_frame, apply_to=['mask'])


def fade_transition(clip: VideoClip, fade_duration: float = 0.5) -> VideoClip:
    """Apply fade in/out to a clip."""
    return clip.fadein(fade_duration).fadeout(fade_duration)


def crossfade(clip1: VideoClip, clip2: VideoClip, duration: float = 0.5) -> VideoClip:
    """Create a crossfade transition between two clips."""
    clip1_fadeout = clip1.fadeout(duration)
    clip2_fadein = clip2.fadein(duration)
    
    # Overlap the clips
    clip2_fadein = clip2_fadein.set_start(clip1.duration - duration)
    
    return CompositeVideoClip([clip1_fadeout, clip2_fadein])


def split_screen(clip1: VideoClip, clip2: VideoClip, position: str = "horizontal") -> VideoClip:
    """
    Create a split-screen effect with two clips.
    
    Args:
        clip1: First clip (left or top)
        clip2: Second clip (right or bottom)
        position: "horizontal" or "vertical"
    """
    w, h = clip1.size
    
    if position == "horizontal":
        # Side by side
        clip1_resized = clip1.resize((w // 2, h))
        clip2_resized = clip2.resize((w // 2, h))
        clip2_resized = clip2_resized.set_position((w // 2, 0))
    else:
        # Top and bottom
        clip1_resized = clip1.resize((w, h // 2))
        clip2_resized = clip2.resize((w, h // 2))
        clip2_resized = clip2_resized.set_position((0, h // 2))
    
    return CompositeVideoClip([clip1_resized, clip2_resized], size=(w, h))
