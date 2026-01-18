"""Video generation endpoints."""
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pathlib import Path
from api.schemas import GenerateRequest, GenerateResponse, StatusResponse, JobStatus, ErrorResponse
from processor.worker import VideoWorker, get_job_status, get_job_result
from utils.logging_config import logger

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_video(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a video from a topic.
    
    Args:
        request: Generation request with topic and parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        Job information with job_id and status
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    logger.info(f"Received generation request: job_id={job_id}, topic={request.topic}")
    
    # Start background task
    worker = VideoWorker()
    background_tasks.add_task(
        worker.process_video,
        job_id=job_id,
        topic=request.topic,
        recipe_type=request.recipe.value,
        duration=request.duration,
        resolution=request.resolution.value,
        output_format=request.output_format
    )
    
    # Estimate time (rough estimate based on recipe)
    estimated_time = 120  # Default 2 minutes
    if request.recipe == "loop10h":
        estimated_time = 600  # 10 minutes for long loops
    
    return GenerateResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        estimated_time=estimated_time,
        message="Video generation started"
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """
    Get status of a video generation job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status information
    """
    status_info = get_job_status(job_id)
    
    if status_info is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return StatusResponse(**status_info)


@router.get("/download/{job_id}")
async def download_video(job_id: str):
    """
    Download completed video.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Video file response
    """
    from fastapi.responses import FileResponse
    
    result = get_job_result(job_id)
    
    if result is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if result.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is not completed. Status: {result.get('status')}"
        )
    
    video_path = result.get("video_path")
    if not video_path or not Path(video_path).exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"video_{job_id}.mp4"
    )
