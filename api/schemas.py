"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RecipeType(str, Enum):
    """Available recipe types."""
    AUTO = "auto"
    BRAINROT = "brainrot"
    NEWS = "news"
    STORIES = "stories"
    AMBIENT = "ambient"
    LOOP10H = "loop10h"


class Resolution(str, Enum):
    """Available resolutions."""
    P1080 = "1080p"
    P720 = "720p"
    VERTICAL = "vertical"


class GenerateRequest(BaseModel):
    """Request schema for video generation."""
    topic: str = Field(..., description="Topic/theme for the video", min_length=1, max_length=500)
    recipe: RecipeType = Field(default=RecipeType.AUTO, description="Recipe type (auto for AI selection)")
    duration: Optional[float] = Field(default=None, description="Video duration in seconds (uses recipe default if not specified)", gt=0)
    output_format: str = Field(default="mp4", description="Output video format")
    resolution: Resolution = Field(default=Resolution.P1080, description="Video resolution")


class JobStatus(str, Enum):
    """Job status values."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerateResponse(BaseModel):
    """Response schema for video generation request."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    estimated_time: Optional[int] = Field(default=None, description="Estimated completion time in seconds")
    message: Optional[str] = Field(default=None, description="Additional message")


class StatusResponse(BaseModel):
    """Response schema for job status check."""
    job_id: str
    status: JobStatus
    progress: Optional[float] = Field(default=None, description="Progress percentage (0-100)")
    message: Optional[str] = None
    video_path: Optional[str] = Field(default=None, description="Path to completed video (if available)")
    error: Optional[str] = Field(default=None, description="Error message (if failed)")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Error details")
