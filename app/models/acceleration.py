from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AccelerationSample(BaseModel):
    """Model for a single accelerometer data sample."""

    timestamp: datetime
    x: float
    y: float
    z: float


class AccelerationData(BaseModel):
    """Model for a collection of accelerometer data samples."""

    data_type: str
    device_info: Dict[str, Any]
    sampling_rate_hz: int
    start_time: datetime
    samples: List[AccelerationSample]
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
