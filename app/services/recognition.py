from typing import List

from app.models.acceleration import AccelerationData
from app.models.activity import (
    ActivityType, ActivityMetrics, ActivitySegment, ActivityPattern,
    ActivityRequest, ActivityResponse
)
from app.utils.metrics import calculate_activity_metrics
from app.utils.patterns import detect_activity_segments, detect_activity_patterns

class ActivityRecognitionService:
    """Service for recognizing activities from accelerometer data."""
    
    def __init__(self):
        # Could initialize ML models or other resources here
        pass
        
    def recognize_activity(self, request: ActivityRequest) -> ActivityResponse:
        """Analyze accelerometer data and detect activity types and patterns."""
        # Calculate overall metrics
        overall_metrics = calculate_activity_metrics(request.acceleration_data)
        
        # Detect activity segments
        activity_segments = detect_activity_segments(request.acceleration_data)
        
        # Determine dominant activity type
        dominant_activity = self._determine_dominant_activity(activity_segments)
        
        # Initialize response
        response = ActivityResponse(
            status="success",
            activity_segments=activity_segments,
            dominant_activity=dominant_activity,
            overall_metrics=overall_metrics,
            activity_patterns=[]
        )
        
        # Generate activity patterns if requested
        if request.include_patterns:
            response.activity_patterns = detect_activity_patterns(
                request.acceleration_data, activity_segments
            )
        
        return response
    
    def _determine_dominant_activity(self, segments: List[ActivitySegment]) -> ActivityType:
        """Determine the dominant activity type from a list of segments."""
        if not segments:
            return ActivityType.UNKNOWN
            
        # Count duration for each activity type
        duration_by_type = {}
        for segment in segments:
            activity_type = segment.activity_type
            duration = (segment.end_time - segment.start_time).total_seconds()
            
            if activity_type not in duration_by_type:
                duration_by_type[activity_type] = 0
            
            duration_by_type[activity_type] += duration
        
        # Find the activity type with the longest duration
        dominant_type = max(duration_by_type.items(), key=lambda x: x[1])[0]
        return dominant_type
    
    def calculate_activity_metrics(self, data: AccelerationData) -> ActivityMetrics:
        """Calculate activity metrics from accelerometer data."""
        return calculate_activity_metrics(data)
    
    def get_supported_activity_types(self) -> List[ActivityType]:
        """Get a list of all supported activity types."""
        return list(ActivityType)