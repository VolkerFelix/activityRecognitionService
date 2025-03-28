from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.models.acceleration import AccelerationData
from app.models.activity import ActivityRequest, ActivityResponse, ActivityType
from app.services.recognition import ActivityRecognitionService

router = APIRouter()
activity_service = ActivityRecognitionService()


@router.post("/recognize", response_model=ActivityResponse)
async def recognize_activity(request: ActivityRequest):
    """Analyze accelerometer data and detect activity types and patterns."""
    try:
        response = activity_service.recognize_activity(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing activity data: {str(e)}"
        )


@router.get("/activity_types", response_model=List[ActivityType])
async def get_activity_types():
    """Get a list of all supported activity types."""
    try:
        return activity_service.get_supported_activity_types()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving activity types: {str(e)}"
        )


@router.post("/metrics", response_model=dict)
async def calculate_activity_metrics(data: AccelerationData):
    """Calculate activity metrics from accelerometer data."""
    try:
        metrics = activity_service.calculate_activity_metrics(data)
        return metrics.dict()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calculating activity metrics: {str(e)}"
        )
