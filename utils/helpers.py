"""
Helper utility functions for the Smart Waste Management System
"""
import json
import os
from datetime import datetime
from typing import Dict, Any
import pandas as pd


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime for display"""
    return dt.strftime(format_str)


def format_weight(kg: float) -> str:
    """Format weight with appropriate units (kg or tons)"""
    if kg >= 1000:
        return f"{kg/1000:.2f} tons"
    return f"{kg:.2f} kg"


def format_currency(amount: float, currency: str = "$") -> str:
    """Format currency with symbol"""
    return f"{currency}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage with % symbol"""
    return f"{value:.{decimals}f}%"


def calculate_time_elapsed(start: datetime, end: datetime) -> float:
    """Calculate hours between two timestamps"""
    delta = end - start
    return delta.total_seconds() / 3600


def load_config(filepath: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='cp1252', errors='replace') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config file with fallback encoding: {e}")
                return {}
    except FileNotFoundError:
        print(f"Config file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}")
        return {}
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {}


def save_config(config: Dict[str, Any], filepath: str = "config.json"):
    """Save configuration to JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def export_to_csv(data: pd.DataFrame, filename: str, directory: str = "exports"):
    """Export data to CSV file"""
    try:
        # Create exports directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        filepath = os.path.join(directory, filename)
        data.to_csv(filepath, index=False)
        return filepath
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None


def get_status_color(status: str) -> str:
    """Get color code for bin status"""
    colors = {
        "Critical": "#D32F2F",
        "Warning": "#F57C00",
        "Partial": "#FDD835",
        "Empty": "#66BB6A"
    }
    return colors.get(status, "#9E9E9E")


def get_alert_priority_color(priority: int) -> str:
    """Get color code for alert priority"""
    colors = {
        1: "#D32F2F",  # Critical - Red
        2: "#F57C00",  # Warning - Orange
        3: "#FDD835",  # Anomaly - Yellow
        4: "#2196F3"   # Info - Blue
    }
    return colors.get(priority, "#9E9E9E")


def calculate_distance_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    Returns distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance


def format_distance(km: float) -> str:
    """Format distance with appropriate units"""
    if km < 1:
        return f"{km * 1000:.0f} m"
    return f"{km:.2f} km"


def format_duration(hours: float) -> str:
    """Format duration in hours to human-readable format"""
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes} min"
    elif hours < 24:
        return f"{hours:.1f} hrs"
    else:
        days = int(hours / 24)
        remaining_hours = hours % 24
        return f"{days}d {remaining_hours:.1f}h"


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate GPS coordinates"""
    return -90 <= lat <= 90 and -180 <= lon <= 180


def get_zone_color(zone: str) -> str:
    """Get color code for zone"""
    colors = {
        "Academic": "#2196F3",
        "Dorm": "#4CAF50",
        "Cafeteria": "#FF9800"
    }
    return colors.get(zone, "#9E9E9E")


def calculate_recycling_rate(recyclable_kg: float, total_kg: float) -> float:
    """Calculate recycling rate as percentage"""
    if total_kg == 0:
        return 0.0
    return (recyclable_kg / total_kg) * 100


def get_date_range_string(start_date: datetime, end_date: datetime) -> str:
    """Format date range for display"""
    if start_date.date() == end_date.date():
        return start_date.strftime("%B %d, %Y")
    return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    if denominator == 0:
        return default
    return numerator / denominator

# Made with Bob
