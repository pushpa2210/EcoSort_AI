"""
Alert System Module - Generate and manage collection alerts
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from modules.bin_monitor import Bin
import pandas as pd


@dataclass
class Alert:
    """Represents a collection alert"""
    bin_id: str
    alert_type: str
    fill_level: float
    message: str
    alert_id: str = field(default_factory=lambda: f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    zone: str = ""
    bin_type: str = ""
    
    @property
    def priority(self) -> int:
        """Calculate priority (1=highest, 4=lowest)"""
        if self.alert_type == "Critical":
            return 1
        elif self.alert_type == "Warning":
            return 2
        elif self.alert_type == "Anomaly":
            return 3
        else:
            return 4
    
    @property
    def priority_color(self) -> str:
        """Get color for priority"""
        colors = {
            1: "#D32F2F",  # Critical - Red
            2: "#F57C00",  # Warning - Orange
            3: "#FDD835",  # Anomaly - Yellow
            4: "#2196F3"   # Info - Blue
        }
        return colors.get(self.priority, "#9E9E9E")
    
    @property
    def age_hours(self) -> float:
        """Get alert age in hours"""
        delta = datetime.now() - self.timestamp
        return delta.total_seconds() / 3600
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'bin_id': self.bin_id,
            'zone': self.zone,
            'bin_type': self.bin_type,
            'alert_type': self.alert_type,
            'fill_level': round(self.fill_level, 1),
            'message': self.message,
            'priority': self.priority,
            'priority_color': self.priority_color,
            'acknowledged': self.acknowledged,
            'age_hours': round(self.age_hours, 1)
        }


def check_bins_for_alerts(bins: List[Bin], config: Dict) -> List[Alert]:
    """
    Check all bins and generate alerts based on thresholds
    
    Args:
        bins: List of Bin objects
        config: Configuration dictionary with alert thresholds
        
    Returns:
        List of Alert objects
    """
    alerts = []
    thresholds = config.get('alerts', {}).get('thresholds', {
        'critical': 90,
        'warning': 75,
        'info': 50
    })
    
    for bin in bins:
        fill_pct = bin.fill_percentage
        
        # Critical alert
        if fill_pct >= thresholds.get('critical', 90):
            alerts.append(Alert(
                bin_id=bin.bin_id,
                zone=bin.zone,
                bin_type=bin.bin_type,
                alert_type="Critical",
                fill_level=fill_pct,
                message=f"Bin {bin.bin_id} is {fill_pct:.1f}% full and requires immediate collection!"
            ))
        
        # Warning alert
        elif fill_pct >= thresholds.get('warning', 75):
            time_to_full = bin.estimated_time_to_full
            time_msg = f" (estimated {time_to_full:.1f}h until full)" if time_to_full else ""
            alerts.append(Alert(
                bin_id=bin.bin_id,
                zone=bin.zone,
                bin_type=bin.bin_type,
                alert_type="Warning",
                fill_level=fill_pct,
                message=f"Bin {bin.bin_id} is {fill_pct:.1f}% full{time_msg}. Schedule collection soon."
            ))
    
    return alerts


def detect_anomalies(bins: List[Bin], historical_data: Optional[pd.DataFrame] = None) -> List[Alert]:
    """
    Detect unusual fill patterns
    
    Args:
        bins: List of Bin objects
        historical_data: Historical waste data (optional)
        
    Returns:
        List of Alert objects for anomalies
    """
    alerts = []
    
    for bin in bins:
        # Check if bin hasn't been emptied in a long time
        if bin.time_since_collection > 48:  # More than 48 hours
            alerts.append(Alert(
                bin_id=bin.bin_id,
                zone=bin.zone,
                bin_type=bin.bin_type,
                alert_type="Anomaly",
                fill_level=bin.fill_percentage,
                message=f"Bin {bin.bin_id} hasn't been collected in {bin.time_since_collection:.1f} hours!"
            ))
        
        # Check for unusually high fill rate
        if bin.fill_rate_kg_per_hour > 0:
            expected_rate = bin.fill_rate_kg_per_hour
            # If bin is filling much faster than expected (simplified check)
            if bin.fill_percentage > 80 and bin.time_since_collection < 12:
                alerts.append(Alert(
                    bin_id=bin.bin_id,
                    zone=bin.zone,
                    bin_type=bin.bin_type,
                    alert_type="Anomaly",
                    fill_level=bin.fill_percentage,
                    message=f"Bin {bin.bin_id} is filling faster than expected. Possible overflow risk."
                ))
    
    return alerts


def get_active_alerts(alerts: List[Alert]) -> List[Alert]:
    """
    Return unacknowledged alerts sorted by priority
    
    Args:
        alerts: List of Alert objects
        
    Returns:
        Sorted list of unacknowledged alerts
    """
    active = [alert for alert in alerts if not alert.acknowledged]
    return sorted(active, key=lambda x: (x.priority, -x.fill_level))


def get_alerts_by_zone(alerts: List[Alert], zone: str) -> List[Alert]:
    """Filter alerts by zone"""
    return [alert for alert in alerts if alert.zone == zone]


def get_alerts_by_type(alerts: List[Alert], alert_type: str) -> List[Alert]:
    """Filter alerts by type"""
    return [alert for alert in alerts if alert.alert_type == alert_type]


def acknowledge_alert(alert_id: str, alerts: List[Alert]) -> bool:
    """
    Mark alert as acknowledged
    
    Args:
        alert_id: Alert ID to acknowledge
        alerts: List of Alert objects
        
    Returns:
        True if alert was found and acknowledged, False otherwise
    """
    for alert in alerts:
        if alert.alert_id == alert_id:
            alert.acknowledged = True
            return True
    return False


def acknowledge_multiple_alerts(alert_ids: List[str], alerts: List[Alert]) -> int:
    """
    Acknowledge multiple alerts
    
    Args:
        alert_ids: List of alert IDs
        alerts: List of Alert objects
        
    Returns:
        Number of alerts acknowledged
    """
    count = 0
    for alert_id in alert_ids:
        if acknowledge_alert(alert_id, alerts):
            count += 1
    return count


def estimate_time_to_overflow(bin: Bin) -> Optional[float]:
    """
    Calculate hours until bin reaches 100% capacity
    
    Args:
        bin: Bin object
        
    Returns:
        Hours until overflow or None if already full or no fill rate
    """
    if bin.fill_percentage >= 100:
        return 0.0
    
    if bin.fill_rate_kg_per_hour <= 0:
        return None
    
    remaining_capacity = bin.capacity_kg - bin.current_fill_kg
    hours_to_full = remaining_capacity / bin.fill_rate_kg_per_hour
    
    return hours_to_full


def get_alert_summary(alerts: List[Alert]) -> Dict:
    """
    Get summary statistics for alerts
    
    Args:
        alerts: List of Alert objects
        
    Returns:
        Dictionary with alert summary
    """
    active_alerts = get_active_alerts(alerts)
    
    type_counts = {
        'Critical': len(get_alerts_by_type(active_alerts, 'Critical')),
        'Warning': len(get_alerts_by_type(active_alerts, 'Warning')),
        'Anomaly': len(get_alerts_by_type(active_alerts, 'Anomaly')),
        'Info': len(get_alerts_by_type(active_alerts, 'Info'))
    }
    
    return {
        'total_alerts': len(alerts),
        'active_alerts': len(active_alerts),
        'acknowledged_alerts': len(alerts) - len(active_alerts),
        'type_counts': type_counts,
        'critical_count': type_counts['Critical'],
        'warning_count': type_counts['Warning']
    }


def generate_collection_schedule(bins: List[Bin], config: Dict) -> List[Dict]:
    """
    Generate recommended collection schedule based on bin status
    
    Args:
        bins: List of Bin objects
        config: Configuration dictionary
        
    Returns:
        List of collection recommendations
    """
    schedule = []
    
    # Get bins that need collection (Critical and Warning)
    critical_bins = [b for b in bins if b.status == "Critical"]
    warning_bins = [b for b in bins if b.status == "Warning"]
    
    # Sort by fill percentage (highest first)
    critical_bins.sort(key=lambda x: x.fill_percentage, reverse=True)
    warning_bins.sort(key=lambda x: x.fill_percentage, reverse=True)
    
    # Add critical bins to schedule (immediate)
    for bin in critical_bins:
        schedule.append({
            'bin_id': bin.bin_id,
            'zone': bin.zone,
            'bin_type': bin.bin_type,
            'fill_percentage': bin.fill_percentage,
            'priority': 'Immediate',
            'recommended_time': 'Now',
            'estimated_time_to_full': bin.estimated_time_to_full
        })
    
    # Add warning bins to schedule (within 24 hours)
    for bin in warning_bins:
        time_to_full = bin.estimated_time_to_full
        if time_to_full and time_to_full < 24:
            recommended = "Within 12 hours"
        else:
            recommended = "Within 24 hours"
        
        schedule.append({
            'bin_id': bin.bin_id,
            'zone': bin.zone,
            'bin_type': bin.bin_type,
            'fill_percentage': bin.fill_percentage,
            'priority': 'High',
            'recommended_time': recommended,
            'estimated_time_to_full': time_to_full
        })
    
    return schedule


def create_info_alert(message: str, bin_id: str = "SYSTEM") -> Alert:
    """
    Create an informational alert
    
    Args:
        message: Alert message
        bin_id: Bin ID (default: SYSTEM)
        
    Returns:
        Alert object
    """
    return Alert(
        bin_id=bin_id,
        alert_type="Info",
        fill_level=0.0,
        message=message
    )


def clear_old_alerts(alerts: List[Alert], max_age_hours: float = 72) -> List[Alert]:
    """
    Remove alerts older than specified age
    
    Args:
        alerts: List of Alert objects
        max_age_hours: Maximum age in hours
        
    Returns:
        Filtered list of alerts
    """
    return [alert for alert in alerts if alert.age_hours <= max_age_hours]


def get_zone_alert_summary(alerts: List[Alert], zone: str) -> Dict:
    """
    Get alert summary for a specific zone
    
    Args:
        alerts: List of Alert objects
        zone: Zone name
        
    Returns:
        Dictionary with zone alert summary
    """
    zone_alerts = get_alerts_by_zone(alerts, zone)
    active = get_active_alerts(zone_alerts)
    
    return {
        'zone': zone,
        'total_alerts': len(zone_alerts),
        'active_alerts': len(active),
        'critical': len([a for a in active if a.alert_type == 'Critical']),
        'warning': len([a for a in active if a.alert_type == 'Warning']),
        'anomaly': len([a for a in active if a.alert_type == 'Anomaly'])
    }

# Made with Bob
