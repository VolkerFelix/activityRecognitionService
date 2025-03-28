import json
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.models.acceleration import AccelerationData, AccelerationSample
from app.models.activity import ActivityRequest, ActivityType

def create_test_acceleration_data(activity_type="walking", duration_seconds=60, sampling_rate=50):
    """Generate synthetic acceleration data for testing."""
    samples = []
    now = datetime.utcnow()
    
    # Generate data specific to the activity type
    for i in range(duration_seconds * sampling_rate):
        timestamp = now + timedelta(milliseconds=i * (1000 / sampling_rate))
        
        if activity_type == "walking":
            # Simulate walking with periodic signals
            time_factor = i / sampling_rate
            x = 0.1 * (i % 5) + 0.05 * (time_factor % 2)  # Small x movement
            y = 0.2 * ((i // 10) % 3) + 0.1 * (time_factor % 1.5)  # Small y movement
            z = 0.9 + 0.05 * (i % 7) + 0.05 * (time_factor % 1)  # Mostly gravity
        elif activity_type == "running":
            # More pronounced movements for running
            time_factor = i / sampling_rate
            x = 0.3 * (i % 5) + 0.2 * (time_factor % 1)
            y = 0.4 * ((i // 10) % 3) + 0.3 * (time_factor % 0.8)
            z = 0.9 + 0.15 * (i % 7) + 0.1 * (time_factor % 0.5)
        elif activity_type == "sitting":
            # Very little movement for sitting
            x = 0.02 * (i % 5) + 0.01 * (i % 3)
            y = 0.02 * ((i // 10) % 3) + 0.01 * (i % 2)
            z = 1.0 + 0.01 * (i % 7)
        else:
            # Default pattern
            x = 0.1 * (i % 5)
            y = 0.1 * ((i // 10) % 3)
            z = 1.0 + 0.02 * (i % 7)

        samples.append(AccelerationSample(
            timestamp=timestamp,
            x=x,
            y=y,
            z=z
        ))
    
    return AccelerationData(
        data_type="acceleration",
        device_info={"device_type": "test", "model": "integration-test"},
        sampling_rate_hz=sampling_rate,
        start_time=now,
        samples=samples,
        id=f"test-data-{uuid.uuid4()}"
    )