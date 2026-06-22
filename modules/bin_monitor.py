"""
Bin Monitor Module - Track and simulate bin fill levels
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random


@dataclass
class Bin:
    """Represents a waste bin on campus"""
    bin_id: str
    zone: str
    location: Dict[str, float]
    capacity_kg: float
    bin_type: str
    current_fill_kg: float = 0.0
    last_collection: datetime = field(default_factory=datetime.now)
    fill_rate_kg_per_hour: float = 0.0
    
    @property
    def fill_percentage(self) -> float:
        """Calculate fill percentage"""
        return min((self.current_fill_kg / self.capacity_kg) * 100, 100)
    
    @property
    def status(self) -> str:
        """Determine bin status based on fill level"""
        if self.fill_percentage >= 90:
            return "Critical"
        elif self.fill_percentage >= 75:
            return "Warning"
        elif self.fill_percentage >= 50:
            return "Partial"
        else:
            return "Empty"
    
    @property
    def status_color(self) -> str:
        """Get color for status"""
        colors = {
            "Critical": "#D32F2F",
            "Warning": "#F57C00",
            "Partial": "#FDD835",
            "Empty": "#66BB6A"
        }
        return colors.get(self.status, "#9E9E9E")
    
    @property
    def time_since_collection(self) -> float:
        """Get hours since last collection"""
        delta = datetime.now() - self.last_collection
        return delta.total_seconds() / 3600
    
    @property
    def estimated_time_to_full(self) -> Optional[float]:
        """Estimate hours until bin is full"""
        if self.fill_rate_kg_per_hour <= 0:
            return None
        
        remaining_capacity = self.capacity_kg - self.current_fill_kg
        if remaining_capacity <= 0:
            return 0
        
        return remaining_capacity / self.fill_rate_kg_per_hour
    
    def update_fill_level(self, hours_elapsed: float):
        """Simulate fill level increase"""
        self.current_fill_kg += self.fill_rate_kg_per_hour * hours_elapsed
        self.current_fill_kg = min(self.current_fill_kg, self.capacity_kg)
    
    def empty_bin(self):
        """Reset bin after collection"""
        self.current_fill_kg = 0.0
        self.last_collection = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'bin_id': self.bin_id,
            'zone': self.zone,
            'location': self.location,
            'capacity_kg': self.capacity_kg,
            'current_fill_kg': round(self.current_fill_kg, 2),
            'fill_percentage': round(self.fill_percentage, 1),
            'bin_type': self.bin_type,
            'status': self.status,
            'status_color': self.status_color,
            'last_collection': self.last_collection.strftime('%Y-%m-%d %H:%M'),
            'time_since_collection_hr': round(self.time_since_collection, 1),
            'estimated_time_to_full_hr': round(self.estimated_time_to_full, 1) if self.estimated_time_to_full else None,
            'fill_rate_kg_per_hour': round(self.fill_rate_kg_per_hour, 3)
        }


def generate_bin_locations(config: Dict) -> Dict[str, Dict[str, float]]:
    """
    Generate sample GPS coordinates for bins
    
    Args:
        config: Configuration dictionary with campus location
        
    Returns:
        Dictionary mapping bin_id to location coordinates
    """
    base_lat = config.get('system', {}).get('campus_location', {}).get('lat', 12.9716)
    base_lon = config.get('system', {}).get('campus_location', {}).get('lon', 77.5946)
    
    locations = {}
    
    # Academic zone bins (15 bins)
    for i in range(1, 16):
        locations[f"A-{i:02d}"] = {
            'lat': base_lat + random.uniform(-0.005, 0.005),
            'lon': base_lon + random.uniform(-0.005, 0.005)
        }
    
    # Dorm zone bins (12 bins)
    for i in range(1, 13):
        locations[f"D-{i:02d}"] = {
            'lat': base_lat + 0.01 + random.uniform(-0.003, 0.003),
            'lon': base_lon + 0.01 + random.uniform(-0.003, 0.003)
        }
    
    # Cafeteria zone bins (8 bins)
    for i in range(1, 9):
        locations[f"C-{i:02d}"] = {
            'lat': base_lat - 0.01 + random.uniform(-0.003, 0.003),
            'lon': base_lon - 0.01 + random.uniform(-0.003, 0.003)
        }
    
    return locations


def initialize_bins(zone_stats: Dict, config: Dict) -> List[Bin]:
    """
    Create bin objects for all campus zones
    
    Args:
        zone_stats: Statistics for each zone from historical data
        config: Configuration dictionary
        
    Returns:
        List of Bin objects
    """
    bins = []
    locations = generate_bin_locations(config)
    
    default_capacity = config.get('bins', {}).get('default_capacity_kg', 100)
    initial_fill_range = config.get('simulation', {}).get('initial_fill_percentage_range', [10, 40])
    
    # Academic zone
    academic_stats = zone_stats.get('Academic', {})
    academic_waste = academic_stats.get('avg_waste_kg', 1200)
    academic_recyclable = academic_stats.get('avg_recyclable_kg', 500)
    
    for i in range(1, 11):  # 10 general bins
        bin_id = f"A-{i:02d}"
        initial_fill = random.uniform(initial_fill_range[0], initial_fill_range[1])
        bins.append(Bin(
            bin_id=bin_id,
            zone="Academic",
            location=locations.get(bin_id, {'lat': 0, 'lon': 0}),
            capacity_kg=default_capacity,
            bin_type="General",
            current_fill_kg=(initial_fill / 100) * default_capacity,
            fill_rate_kg_per_hour=academic_waste / 24 / 10
        ))
    
    for i in range(11, 16):  # 5 recyclable bins
        bin_id = f"A-{i:02d}"
        initial_fill = random.uniform(initial_fill_range[0], initial_fill_range[1])
        bins.append(Bin(
            bin_id=bin_id,
            zone="Academic",
            location=locations.get(bin_id, {'lat': 0, 'lon': 0}),
            capacity_kg=default_capacity,
            bin_type="Recyclable",
            current_fill_kg=(initial_fill / 100) * default_capacity,
            fill_rate_kg_per_hour=academic_recyclable / 24 / 5
        ))
    
    # Dorm zone
    dorm_stats = zone_stats.get('Dorm', {})
    dorm_waste = dorm_stats.get('avg_waste_kg', 800)
    dorm_recyclable = dorm_stats.get('avg_recyclable_kg', 300)
    
    for i in range(1, 9):  # 8 general bins
        bin_id = f"D-{i:02d}"
        initial_fill = random.uniform(initial_fill_range[0], initial_fill_range[1])
        bins.append(Bin(
            bin_id=bin_id,
            zone="Dorm",
            location=locations.get(bin_id, {'lat': 0, 'lon': 0}),
            capacity_kg=default_capacity,
            bin_type="General",
            current_fill_kg=(initial_fill / 100) * default_capacity,
            fill_rate_kg_per_hour=dorm_waste / 24 / 8
        ))
    
    for i in range(9, 13):  # 4 recyclable bins
        bin_id = f"D-{i:02d}"
        initial_fill = random.uniform(initial_fill_range[0], initial_fill_range[1])
        bins.append(Bin(
            bin_id=bin_id,
            zone="Dorm",
            location=locations.get(bin_id, {'lat': 0, 'lon': 0}),
            capacity_kg=default_capacity,
            bin_type="Recyclable",
            current_fill_kg=(initial_fill / 100) * default_capacity,
            fill_rate_kg_per_hour=dorm_recyclable / 24 / 4
        ))
    
    # Cafeteria zone
    cafeteria_stats = zone_stats.get('Cafeteria', {})
    cafeteria_waste = cafeteria_stats.get('avg_waste_kg', 600)
    cafeteria_recyclable = cafeteria_stats.get('avg_recyclable_kg', 200)
    
    for i in range(1, 6):  # 5 general bins
        bin_id = f"C-{i:02d}"
        initial_fill = random.uniform(initial_fill_range[0], initial_fill_range[1])
        bins.append(Bin(
            bin_id=bin_id,
            zone="Cafeteria",
            location=locations.get(bin_id, {'lat': 0, 'lon': 0}),
            capacity_kg=default_capacity,
            bin_type="General",
            current_fill_kg=(initial_fill / 100) * default_capacity,
            fill_rate_kg_per_hour=cafeteria_waste / 24 / 5
        ))
    
    for i in range(6, 9):  # 3 recyclable bins
        bin_id = f"C-{i:02d}"
        initial_fill = random.uniform(initial_fill_range[0], initial_fill_range[1])
        bins.append(Bin(
            bin_id=bin_id,
            zone="Cafeteria",
            location=locations.get(bin_id, {'lat': 0, 'lon': 0}),
            capacity_kg=default_capacity,
            bin_type="Recyclable",
            current_fill_kg=(initial_fill / 100) * default_capacity,
            fill_rate_kg_per_hour=cafeteria_recyclable / 24 / 3
        ))
    
    return bins


def simulate_real_time_fill(bins: List[Bin], last_update: datetime) -> datetime:
    """
    Update all bin fill levels based on time elapsed
    
    Args:
        bins: List of Bin objects
        last_update: Timestamp of last update
        
    Returns:
        Current timestamp
    """
    current_time = datetime.now()
    hours_elapsed = (current_time - last_update).total_seconds() / 3600
    
    for bin in bins:
        bin.update_fill_level(hours_elapsed)
    
    return current_time


def get_bins_by_status(bins: List[Bin], status: str) -> List[Bin]:
    """Filter bins by status"""
    return [bin for bin in bins if bin.status == status]


def get_bins_by_zone(bins: List[Bin], zone: str) -> List[Bin]:
    """Filter bins by zone"""
    return [bin for bin in bins if bin.zone == zone]


def get_bins_by_type(bins: List[Bin], bin_type: str) -> List[Bin]:
    """Filter bins by type"""
    return [bin for bin in bins if bin.bin_type == bin_type]


def get_critical_bins(bins: List[Bin], threshold: float = 90) -> List[Bin]:
    """Get bins requiring immediate attention"""
    return [bin for bin in bins if bin.fill_percentage >= threshold]


def get_bin_by_id(bins: List[Bin], bin_id: str) -> Optional[Bin]:
    """Get a specific bin by ID"""
    for bin in bins:
        if bin.bin_id == bin_id:
            return bin
    return None


def get_zone_summary(bins: List[Bin], zone: str) -> Dict:
    """
    Get summary statistics for a zone
    
    Args:
        bins: List of all bins
        zone: Zone name
        
    Returns:
        Dictionary with zone summary
    """
    zone_bins = get_bins_by_zone(bins, zone)
    
    if not zone_bins:
        return {}
    
    total_capacity = sum(b.capacity_kg for b in zone_bins)
    total_fill = sum(b.current_fill_kg for b in zone_bins)
    avg_fill_pct = sum(b.fill_percentage for b in zone_bins) / len(zone_bins)
    
    return {
        'zone': zone,
        'total_bins': len(zone_bins),
        'total_capacity_kg': total_capacity,
        'total_fill_kg': total_fill,
        'avg_fill_percentage': avg_fill_pct,
        'critical_bins': len([b for b in zone_bins if b.status == "Critical"]),
        'warning_bins': len([b for b in zone_bins if b.status == "Warning"]),
        'general_bins': len([b for b in zone_bins if b.bin_type == "General"]),
        'recyclable_bins': len([b for b in zone_bins if b.bin_type == "Recyclable"])
    }


def get_overall_summary(bins: List[Bin]) -> Dict:
    """
    Get overall system summary
    
    Args:
        bins: List of all bins
        
    Returns:
        Dictionary with overall summary
    """
    if not bins:
        return {}
    
    total_capacity = sum(b.capacity_kg for b in bins)
    total_fill = sum(b.current_fill_kg for b in bins)
    avg_fill_pct = sum(b.fill_percentage for b in bins) / len(bins)
    
    status_counts = {
        'Critical': len(get_bins_by_status(bins, 'Critical')),
        'Warning': len(get_bins_by_status(bins, 'Warning')),
        'Partial': len(get_bins_by_status(bins, 'Partial')),
        'Empty': len(get_bins_by_status(bins, 'Empty'))
    }
    
    return {
        'total_bins': len(bins),
        'total_capacity_kg': total_capacity,
        'total_fill_kg': total_fill,
        'avg_fill_percentage': avg_fill_pct,
        'status_counts': status_counts,
        'bins_needing_collection': status_counts['Critical'] + status_counts['Warning']
    }

# Made with Bob
