import json
from datetime import datetime, timedelta
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.models.activity import ActivityRequest, ActivityType
from app.models.acceleration import AccelerationData

from tests.integration.common import create_test_acceleration_data

client = TestClient(app)


def test_recognize_activity_walking():
    """Test activity recognition for walking data."""
    # Create test data for walking
    accel_data = create_test_acceleration_data(
        activity_type="walking", duration_seconds=30
    )

    # Create request
    request = ActivityRequest(
        acceleration_data=accel_data,
        include_metrics=True,
        include_patterns=True,
        user_id="test-user-1",
    )

    # Convert to dict for JSON serialization
    request_dict = json.loads(request.json())

    # Call the endpoint
    response = client.post("/api/recognize", json=request_dict)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["activity_segments"]) > 0

    # Check if walking was detected
    found_walking = False
    for segment in data["activity_segments"]:
        if segment["activity_type"] == ActivityType.WALKING:
            found_walking = True
            break

    assert found_walking, "Walking activity should be detected"
    assert data["dominant_activity"] == ActivityType.WALKING
    assert data["overall_metrics"] is not None


def test_recognize_activity_sitting():
    """Test activity recognition for sitting data."""
    # Create test data for sitting
    accel_data = create_test_acceleration_data(
        activity_type="sitting", duration_seconds=30
    )

    # Create request
    request = ActivityRequest(
        acceleration_data=accel_data,
        include_metrics=True,
        include_patterns=True,
        user_id="test-user-2",
    )

    # Convert to dict for JSON serialization
    request_dict = json.loads(request.json())

    # Call the endpoint
    response = client.post("/api/recognize", json=request_dict)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    # Check if sitting was detected
    found_sitting = False
    for segment in data["activity_segments"]:
        if (
            segment["activity_type"] == ActivityType.SITTING
            or segment["activity_type"] == ActivityType.STANDING
        ):
            found_sitting = True
            break

    assert found_sitting, "Sitting or standing activity should be detected"

    # Check metrics for sitting (should be low intensity)
    assert data["overall_metrics"]["avg_intensity"] < 0.3
    assert data["overall_metrics"]["peak_intensity"] < 0.5


def test_recognize_activity_mixed():
    """Test activity recognition with mixed activity data."""
    # Create first half with walking data
    walking_data = create_test_acceleration_data(
        activity_type="walking", duration_seconds=15
    )

    # Create second half with sitting data
    sitting_data = create_test_acceleration_data(
        activity_type="sitting", duration_seconds=15
    )

    # Combine the samples and adjust timestamps for the sitting data
    time_offset = (
        walking_data.samples[-1].timestamp
        - sitting_data.samples[0].timestamp
        + timedelta(seconds=1)
    )
    for sample in sitting_data.samples:
        sample.timestamp += time_offset

    combined_samples = walking_data.samples + sitting_data.samples

    # Create combined acceleration data
    combined_data = AccelerationData(
        data_type="acceleration",
        device_info={"device_type": "test", "model": "integration-test"},
        sampling_rate_hz=walking_data.sampling_rate_hz,
        start_time=walking_data.start_time,
        samples=combined_samples,
        id=f"test-data-{uuid.uuid4()}",
    )

    # Create request
    request = ActivityRequest(
        acceleration_data=combined_data,
        include_metrics=True,
        include_patterns=True,
        user_id="test-user-3",
    )

    # Convert to dict for JSON serialization
    request_dict = json.loads(request.json())

    # Call the endpoint
    response = client.post("/api/recognize", json=request_dict)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    # Should detect multiple segments with different activities
    segments = data["activity_segments"]
    assert len(segments) > 1, "Should detect multiple activity segments"

    # Should detect patterns
    assert (
        len(data["activity_patterns"]) > 0
    ), "Should detect activity patterns with mixed data"


def test_calculate_activity_metrics():
    """Test the activity metrics calculation endpoint."""
    # Create test data
    accel_data = create_test_acceleration_data(
        activity_type="walking", duration_seconds=20
    )

    # Convert to dict for JSON serialization
    data_dict = json.loads(accel_data.json())

    # Call the endpoint
    response = client.post("/api/metrics", json=data_dict)

    # Verify response
    assert response.status_code == 200
    metrics = response.json()

    # Check metrics
    assert "avg_intensity" in metrics
    assert "peak_intensity" in metrics
    assert "movement_consistency" in metrics
    assert "active_minutes" in metrics
    assert "total_duration" in metrics

    # Check valid ranges
    assert 0 <= metrics["avg_intensity"] <= 1.0
    assert 0 <= metrics["peak_intensity"] <= 1.0
    assert 0 <= metrics["movement_consistency"] <= 1.0
    assert metrics["active_minutes"] >= 0
    assert metrics["total_duration"] > 0


def test_get_activity_types():
    """Test retrieving the list of supported activity types."""
    response = client.get("/api/activity_types")

    assert response.status_code == 200
    types = response.json()

    # Verify all expected activity types are present
    expected_types = [
        "walking",
        "running",
        "standing",
        "sitting",
        "lying",
        "cycling",
        "unknown",
    ]
    for activity_type in expected_types:
        assert (
            activity_type in types
        ), f"Activity type '{activity_type}' should be in the list"


def test_empty_data_handling():
    """Test handling of empty acceleration data."""
    # Create empty acceleration data
    empty_data = AccelerationData(
        data_type="acceleration",
        device_info={"device_type": "test", "model": "integration-test"},
        sampling_rate_hz=50,
        start_time=datetime.utcnow(),
        samples=[],
        id=f"test-data-{uuid.uuid4()}",
    )

    # Create request with empty data
    request = ActivityRequest(
        acceleration_data=empty_data,
        include_metrics=True,
        include_patterns=True,
        user_id="test-user-empty",
    )

    # Convert to dict for JSON serialization
    request_dict = json.loads(request.json())

    # Call the endpoint
    response = client.post("/api/recognize", json=request_dict)

    # Verify response (should still succeed but with empty results)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["activity_segments"]) == 0
    assert data["dominant_activity"] == ActivityType.UNKNOWN

    # Metrics should have default values
    assert data["overall_metrics"]["avg_intensity"] == 0.0
    assert data["overall_metrics"]["peak_intensity"] == 0.0
    assert data["overall_metrics"]["active_minutes"] == 0.0


def test_invalid_data_error_handling():
    """Test error handling for invalid acceleration data."""
    # Create request with invalid data structure
    invalid_request = {
        "acceleration_data": {
            "data_type": "acceleration",
            "device_info": {"device_type": "test"},
            # Missing required fields
            "samples": [],
        },
        "user_id": "test-user-invalid",
    }

    # Call the endpoint
    response = client.post("/api/recognize", json=invalid_request)

    # Verify response code indicates validation error
    assert (
        response.status_code == 422
    ), "Should return validation error for invalid data"
