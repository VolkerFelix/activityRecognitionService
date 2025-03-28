from datetime import datetime, timedelta
from typing import List
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

from app.models.acceleration import AccelerationData
from app.models.activity import ActivityType, ActivitySegment, ActivityPattern, ActivityMetrics
from app.utils.metrics import calculate_activity_metrics
from app.core.config import settings

def extract_features(data: AccelerationData):
    """Extract features from acceleration data for activity recognition."""
    # This would typically involve calculating various time and frequency domain features
    # from raw acceleration data, like mean, variance, FFT components, etc.
    # Simplified version for demonstration:
    
    samples = data.samples
    window_size = min(20, len(samples))  # Use smaller window for shorter data
    
    if len(samples) < window_size:
        return []
    
    features = []
    for i in range(0, len(samples) - window_size + 1, window_size // 2):  # 50% overlap
        window = samples[i:i+window_size]
        
        # Extract basic features
        x_values = [s.x for s in window]
        y_values = [s.y for s in window]
        z_values = [s.z for s in window]
        
        # Calculate mean, variance, etc.
        feature_vector = {
            'mean_x': np.mean(x_values),
            'mean_y': np.mean(y_values),
            'mean_z': np.mean(z_values),
            'var_x': np.var(x_values),
            'var_y': np.var(y_values),
            'var_z': np.var(z_values),
            'mean_mag': np.mean([np.sqrt(s.x**2 + s.y**2 + s.z**2) for s in window]),
            'start_time': window[0].timestamp,
            'end_time': window[-1].timestamp
        }
        
        features.append(feature_vector)
    
    return features

def classify_activity(features):
    """Classify activity type based on features."""
    # In a real implementation, this would use a trained machine learning model
    # Simplified logic for demonstration purposes:
    
    if not features:
        return ActivityType.UNKNOWN, 0.5
    
    mean_mag = features['mean_mag']
    var_x = features['var_x']
    var_y = features['var_y']
    var_z = features['var_z']
    
    # Simple rule-based classification
    if mean_mag < 1.05 and var_x < 0.01 and var_y < 0.01 and var_z < 0.01:
        return ActivityType.STANDING, 0.8
    elif mean_mag < 1.05 and var_x < 0.02 and var_y < 0.02 and var_z < 0.02:
        return ActivityType.SITTING, 0.8
    elif mean_mag < 1.05 and var_x < 0.05 and var_y < 0.05 and var_z < 0.05:
        return ActivityType.LYING, 0.7
    elif 1.1 < mean_mag < 1.5 and 0.05 < (var_x + var_y + var_z) < 0.3:
        return ActivityType.WALKING, 0.9
    elif mean_mag > 1.5 and (var_x + var_y + var_z) > 0.3:
        return ActivityType.RUNNING, 0.85
    elif 1.1 < mean_mag < 1.8 and 0.1 < var_x < 0.5 and 0.1 < var_y < 0.5:
        return ActivityType.CYCLING, 0.75
    else:
        return ActivityType.UNKNOWN, 0.5

def detect_activity_segments(data: AccelerationData) -> List[ActivitySegment]:
    """Detect activity segments from acceleration data."""
    features_list = extract_features(data)
    
    if not features_list:
        return []
    
    segments = []
    current_activity = None
    segment_start = None
    segment_features = []
    
    for features in features_list:
        activity_type, confidence = classify_activity(features)
        
        # Start a new segment if activity changes
        if current_activity != activity_type or not current_activity:
            # Save the previous segment if it exists
            if current_activity and segment_start:
                # Calculate metrics for the segment
                segment_data = AccelerationData(
                    data_type=data.data_type,
                    device_info=data.device_info,
                    sampling_rate_hz=data.sampling_rate_hz,
                    start_time=segment_start,
                    samples=[s for s in data.samples if segment_start <= s.timestamp <= features['start_time']]
                )
                
                metrics = calculate_activity_metrics(segment_data)
                
                segments.append(ActivitySegment(
                    start_time=segment_start,
                    end_time=features['start_time'],
                    activity_type=current_activity,
                    confidence=confidence,
                    metrics=metrics
                ))
            
            # Start a new segment
            current_activity = activity_type
            segment_start = features['start_time']
            segment_features = [features]
        else:
            # Continue current segment
            segment_features.append(features)
    
    # Don't forget the last segment
    if current_activity and segment_start and segment_features:
        last_time = segment_features[-1]['end_time']
        
        # Calculate metrics for the last segment
        segment_data = AccelerationData(
            data_type=data.data_type,
            device_info=data.device_info,
            sampling_rate_hz=data.sampling_rate_hz,
            start_time=segment_start,
            samples=[s for s in data.samples if segment_start <= s.timestamp <= last_time]
        )
        
        metrics = calculate_activity_metrics(segment_data)
        
        segments.append(ActivitySegment(
            start_time=segment_start,
            end_time=last_time,
            activity_type=current_activity,
            confidence=0.7,  # Default confidence for final segment
            metrics=metrics
        ))
    
    return segments

def detect_activity_patterns(
    data: AccelerationData, 
    segments: List[ActivitySegment]
) -> List[ActivityPattern]:
    """Detect activity patterns from a list of activity segments."""
    if not segments:
        return []
    
    patterns = []
    
    # Check for sedentary pattern (long periods of sitting/standing/lying)
    sedentary_segments = [
        s for s in segments 
        if s.activity_type in [ActivityType.SITTING, ActivityType.STANDING, ActivityType.LYING]
    ]
    
    if sedentary_segments:
        total_sedentary_duration = sum(
            [(s.end_time - s.start_time).total_seconds() for s in sedentary_segments]
        ) / 60.0  # Convert to minutes
        
        if total_sedentary_duration > 30:  # More than 30 minutes
            patterns.append(ActivityPattern(
                pattern_type="sedentary",
                description="Extended period of low activity",
                total_duration=total_sedentary_duration,
                segments=sedentary_segments
            ))
    
    # Check for active pattern (walking/running/cycling)
    active_segments = [
        s for s in segments 
        if s.activity_type in [ActivityType.WALKING, ActivityType.RUNNING, ActivityType.CYCLING]
    ]
    
    if active_segments:
        total_active_duration = sum(
            [(s.end_time - s.start_time).total_seconds() for s in active_segments]
        ) / 60.0  # Convert to minutes
        
        if total_active_duration > 10:  # More than 10 minutes
            patterns.append(ActivityPattern(
                pattern_type="active",
                description="Period of sustained activity",
                total_duration=total_active_duration,
                segments=active_segments
            ))
    
    # Check for alternating pattern (frequent transitions between activity types)
    if len(segments) > 5:  # Multiple segments
        unique_activities = len(set([s.activity_type for s in segments]))
        if unique_activities >= 3:  # At least 3 different activity types
            patterns.append(ActivityPattern(
                pattern_type="mixed",
                description="Varied activity with multiple transitions",
                total_duration=sum([(s.end_time - s.start_time).total_seconds() for s in segments]) / 60.0,
                segments=segments
            ))
    
    return patterns