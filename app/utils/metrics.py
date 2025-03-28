from datetime import datetime

import numpy as np
import pandas as pd

from app.core.config import settings
from app.models.acceleration import AccelerationData
from app.models.activity import ActivityMetrics


def calculate_activity_metrics(data: AccelerationData) -> ActivityMetrics:
    """Calculate activity metrics from accelerometer data."""
    samples = data.samples

    if not samples:
        return ActivityMetrics(
            avg_intensity=0.0,
            peak_intensity=0.0,
            movement_consistency=0.0,
            active_minutes=0.0,
            total_duration=0.0,
        )

    # Convert samples to DataFrame for easier manipulation
    df = pd.DataFrame(
        [
            {
                "timestamp": s.timestamp,
                "x": s.x,
                "y": s.y,
                "z": s.z,
            }
            for s in samples
        ]
    )

    # Calculate magnitude of acceleration vector
    df["magnitude"] = np.sqrt(df["x"] ** 2 + df["y"] ** 2 + df["z"] ** 2)

    # Earth's gravity is approximately 1.0 in normalized device values
    gravity_offset = 1.0

    # Calculate metrics
    avg_magnitude = df["magnitude"].mean()
    max_magnitude = df["magnitude"].max()

    # Calculate intensity using a more sensitive scale
    avg_intensity = min(max(0, (avg_magnitude - gravity_offset) / 0.5), 1.0)
    peak_intensity = min(max(0, (max_magnitude - gravity_offset) / 0.5), 1.0)

    # Calculate movement consistency as inverse of variance (normalized)
    magnitude_variance = df["magnitude"].var() if len(df) > 1 else 0
    movement_consistency = max(0, 1 - min(1, magnitude_variance / 2.0))

    # Calculate duration
    start_time = df["timestamp"].min()
    end_time = df["timestamp"].max()
    duration_seconds = (end_time - start_time).total_seconds()
    total_duration = duration_seconds / 60.0  # Convert to minutes

    # Calculate active minutes
    active_threshold = settings.ACTIVITY_DETECTION_THRESHOLD
    # Create a rolling window to detect active periods
    window_size = min(10, len(df))  # Ensure window size doesn't exceed dataframe length
    if window_size > 0:
        df["active"] = df["magnitude"].rolling(
            window=window_size, min_periods=1
        ).mean() > (gravity_offset + active_threshold)
        active_samples = df["active"].sum()
    else:
        active_samples = 0

    # Convert active samples to minutes based on sampling rate
    sample_duration = 1.0 / max(1, data.sampling_rate_hz)  # Avoid division by zero
    active_minutes = (active_samples * sample_duration) / 60.0

    return ActivityMetrics(
        avg_intensity=float(avg_intensity),
        peak_intensity=float(peak_intensity),
        movement_consistency=float(movement_consistency),
        active_minutes=float(active_minutes),
        total_duration=float(total_duration),
    )
