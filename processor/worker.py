"""Background worker for video generation jobs."""
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from utils.config import Config
from utils.logging_config import logger
from recipes.recipe_manager import recipe_manager
from director.selector import get_director_selector
from voice.edge_tts_wrapper import generate_speech_for_recipe
from processor.renderer import VideoRenderer
from processor.ffmpeg_looper import get_ffmpeg_looper


# In-memory job storage (in production, use Redis or database)
_job_storage: Dict[str, Dict] = {}


class VideoWorker:
    """Background worker for processing video generation jobs."""
    
    def __init__(self):
        """Initialize video worker."""
        self.director = get_director_selector()
        self.renderer = VideoRenderer()
        self.ffmpeg_looper = get_ffmpeg_looper()
    
    def process_video(
        self,
        job_id: str,
        topic: str,
        recipe_type: str = "auto",
        duration: Optional[float] = None,
        resolution: str = "1080p",
        output_format: str = "mp4"
    ):
        """
        Process video generation job.
        
        Args:
            job_id: Unique job identifier
            topic: Video topic
            recipe_type: Recipe type or "auto"
            duration: Optional duration override
            resolution: Video resolution
            output_format: Output format
        """
        try:
            # Update job status
            self._update_job_status(job_id, "processing", progress=0.0, message="Starting video generation")
            
            # Step 1: Select recipe
            logger.info(f"[{job_id}] Step 1: Selecting recipe")
            recipe_selection = self.director.select_recipe(topic, recipe_type)
            selected_recipe_name = recipe_selection["recipe"]
            logger.info(f"[{job_id}] Selected recipe: {selected_recipe_name} - {recipe_selection['reasoning']}")
            
            self._update_job_status(job_id, "processing", progress=10.0, message=f"Selected recipe: {selected_recipe_name}")
            
            # Step 2: Get recipe instance
            recipe = recipe_manager.get_recipe(
                selected_recipe_name,
                duration=duration,
                resolution=resolution
            )
            
            # Step 3: Generate story/script
            logger.info(f"[{job_id}] Step 2: Generating story")
            story_text = self.director.generate_story(topic, selected_recipe_name)
            logger.info(f"[{job_id}] Generated story: {story_text[:100]}...")
            
            self._update_job_status(job_id, "processing", progress=20.0, message="Story generated")
            
            # Step 4: Generate TTS narration
            logger.info(f"[{job_id}] Step 3: Generating voice narration")
            narration_path = Config.TEMP_PATH / f"narration_{job_id}.mp3"
            
            try:
                narration_path = generate_speech_for_recipe(
                    story_text,
                    selected_recipe_name,
                    narration_path
                )
                logger.info(f"[{job_id}] Generated narration: {narration_path}")
            except Exception as e:
                logger.warning(f"[{job_id}] TTS generation failed: {e}, continuing without narration")
                narration_path = None
            
            self._update_job_status(job_id, "processing", progress=40.0, message="Voice narration generated")
            
            # Step 5: Render video
            logger.info(f"[{job_id}] Step 4: Rendering video")
            output_path = Config.OUTPUT_PATH / f"video_{job_id}.{output_format}"
            
            if narration_path and narration_path.exists():
                narration_audio = narration_path
            else:
                narration_audio = Path("/dev/null")  # Dummy path if no narration
            
            video_path = self.renderer.render_video(
                recipe=recipe,
                topic=topic,
                story_text=story_text,
                narration_audio=narration_audio if narration_path else Path("/dev/null"),
                output_path=output_path
            )
            
            self._update_job_status(job_id, "processing", progress=80.0, message="Video rendered")
            
            # Step 6: Apply looping if needed (for 10-hour loops)
            if selected_recipe_name == "loop10h":
                logger.info(f"[{job_id}] Step 5: Creating 10-hour loop")
                looped_path = Config.OUTPUT_PATH / f"video_{job_id}_looped.{output_format}"
                video_path = self.ffmpeg_looper.create_loop(
                    video_path,
                    looped_path,
                    target_duration=recipe.duration,
                    seamless=True
                )
                self._update_job_status(job_id, "processing", progress=95.0, message="Loop created")
            
            # Step 7: Complete
            logger.info(f"[{job_id}] Video generation completed: {video_path}")
            self._update_job_status(
                job_id,
                "completed",
                progress=100.0,
                message="Video generation completed",
                video_path=str(video_path)
            )
            
        except Exception as e:
            logger.error(f"[{job_id}] Video generation failed: {e}", exc_info=True)
            self._update_job_status(
                job_id,
                "failed",
                message=f"Generation failed: {str(e)}",
                error=str(e)
            )
    
    def _update_job_status(
        self,
        job_id: str,
        status: str,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        video_path: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Update job status in storage."""
        if job_id not in _job_storage:
            _job_storage[job_id] = {
                "job_id": job_id,
                "status": status,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        _job_storage[job_id]["status"] = status
        _job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        if progress is not None:
            _job_storage[job_id]["progress"] = progress
        
        if message is not None:
            _job_storage[job_id]["message"] = message
        
        if video_path is not None:
            _job_storage[job_id]["video_path"] = video_path
        
        if error is not None:
            _job_storage[job_id]["error"] = error


def get_job_status(job_id: str) -> Optional[Dict]:
    """Get job status from storage."""
    return _job_storage.get(job_id)


def get_job_result(job_id: str) -> Optional[Dict]:
    """Get job result (same as status for now)."""
    return _job_storage.get(job_id)
