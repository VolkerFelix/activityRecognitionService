import json
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
import uuid
import math
import random

from app.main import app
from app.models.acceleration import AccelerationData, AccelerationSample
from app.models.activity import ActivityRequest, ActivityType


def create_test_acceleration_data(
    activity_type="walking", duration_seconds=60, sampling_rate=50
):
    """Generate synthetic acceleration data for testing."""
    samples = []
    now = datetime.utcnow()

    # Generate data specific to the activity type
    for i in range(duration_seconds * sampling_rate):
        timestamp = now + timedelta(milliseconds=i * (1000 / sampling_rate))

        if activity_type == "walking":
            # Simulate walking with more pronounced periodic signals
            time_factor = i / sampling_rate

            # Create more distinctive walking pattern with clearer periodic motion
            # Walking typically has a clear periodic signal in the 1-2 Hz range
            # with vertical acceleration changes (z-axis) and some lateral movement
            period = 2.0  # 2 second gait cycle
            step_phase = (time_factor % period) / period  # 0 to 1 phase

            # More pronounced acceleration changes during walking
            x = 0.2 * math.sin(2 * math.pi * step_phase)  # Lateral sway
            y = 0.1 * math.sin(4 * math.pi * step_phase)  # Forward movement
            z = 1.0 + 0.3 * math.sin(2 * math.pi * step_phase)  # Vertical movement

            # Add some noise
            x += 0.05 * (random.random() - 0.5)
            y += 0.05 * (random.random() - 0.5)
            z += 0.05 * (random.random() - 0.5)

        elif activity_type == "running":
            # More pronounced movements for running
            time_factor = i / sampling_rate
            period = 1.0  # 1 second running cycle (faster than walking)
            step_phase = (time_factor % period) / period

            x = 0.4 * math.sin(2 * math.pi * step_phase)
            y = 0.2 * math.sin(4 * math.pi * step_phase)
            z = 1.0 + 0.6 * math.sin(2 * math.pi * step_phase)

            # Add some noise
            x += 0.1 * (random.random() - 0.5)
            y += 0.1 * (random.random() - 0.5)
            z += 0.1 * (random.random() - 0.5)

        elif activity_type == "sitting":
            # Very little movement for sitting
            x = 0.02 * (random.random() - 0.5)
            y = 0.02 * (random.random() - 0.5)
            z = 1.0 + 0.01 * (random.random() - 0.5)
        else:
            # Default pattern
            x = 0.1 * (i % 5) / 5.0
            y = 0.1 * ((i // 10) % 3) / 3.0
            z = 1.0 + 0.02 * (i % 7) / 7.0

        samples.append(AccelerationSample(timestamp=timestamp, x=x, y=y, z=z))

    return AccelerationData(
        data_type="acceleration",
        device_info={"device_type": "test", "model": "integration-test"},
        sampling_rate_hz=sampling_rate,
        start_time=now,
        samples=samples,
        id=f"test-data-{uuid.uuid4()}",
    )
