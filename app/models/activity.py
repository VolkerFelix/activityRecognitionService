from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.models.acceleration import AccelerationData

class ActivityType(str, Enum):
    WALKING = "walking"
    RUNNING = "running"
    STANDING = "standing"
    SITTING = "sitting"
    LYING = "lying"
    CYCLING = "cycling"
    UNKNOWN = "unknown"

class ActivityMetrics(BaseModel):
    """Model for activity metrics calculated from accelerometer data."""
    avg_intensity: float
    peak_intensity: float
    movement_consistency: float
    active_minutes: float
    total_duration: float

class ActivitySegment(BaseModel):
    """Model for a segment of detected activity."""
    start_time: datetime
    end_time: datetime
    activity_type: ActivityType
    confidence: float
    metrics: ActivityMetrics
    
class ActivityPattern(BaseModel):
    """Model for activity patterns detected across multiple segments."""
    pattern_type: str  # e.g., "sedentary", "active", "mixed"
    description: str
    total_duration: float
    segments: List[ActivitySegment]

class ActivityRequest(BaseModel):
    """Model for a request to analyze activity data."""
    acceleration_data: AccelerationData
    include_metrics: bool = True
    include_patterns: bool = True
    user_id: str

class ActivityResponse(BaseModel):
    """Model for a response containing activity analysis results."""
    status: str
    message: Optional[str] = None
    activity_segments: List[ActivitySegment] = []
    activity_patterns: List[ActivityPattern] = []
    dominant_activity: ActivityType = ActivityType.UNKNOWN
    overall_metrics: Optional[ActivityMetrics] = None