"""
Route Optimizer Module - Optimize waste collection routes
"""
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime
import math


def calculate_distance(loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula
    
    Args:
        loc1: Dictionary with 'lat' and 'lon' keys
        loc2: Dictionary with 'lat' and 'lon' keys
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1 = math.radians(loc1['lat']), math.radians(loc1['lon'])
    lat2, lon2 = math.radians(loc2['lat']), math.radians(loc2['lon'])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def nearest_neighbor_tsp(bins: List, depot: Dict[str, float]) -> Tuple[List[str], float]:
    """
    Solve TSP using Nearest Neighbor heuristic
    
    Args:
        bins: List of Bin objects to collect
        depot: Depot location {'lat': float, 'lon': float}
        
    Returns:
        Tuple of (route as list of bin_ids, total_distance)
    """
    if not bins:
        return [], 0.0
    
    unvisited = bins.copy()
    route = []
    total_distance = 0.0
    current_location = depot
    
    while unvisited:
        # Find nearest unvisited bin
        nearest_bin = None
        min_distance = float('inf')
        
        for bin in unvisited:
            distance = calculate_distance(current_location, bin.location)
            if distance < min_distance:
                min_distance = distance
                nearest_bin = bin
        
        # Visit nearest bin (check if found)
        if nearest_bin is not None:
            route.append(nearest_bin.bin_id)
            total_distance += min_distance
            current_location = nearest_bin.location
            unvisited.remove(nearest_bin)
        else:
            # Safety break if no bin found (shouldn't happen)
            break
    
    # Return to depot
    total_distance += calculate_distance(current_location, depot)
    
    return route, total_distance


def optimize_collection_route(bins: List, depot: Dict[str, float], 
                              truck_capacity_kg: float = 2100) -> Dict:
    """
    Optimize collection route considering truck capacity
    
    Args:
        bins: List of Bin objects needing collection
        depot: Depot location
        truck_capacity_kg: Maximum truck capacity
        
    Returns:
        Dictionary with route information
    """
    if not bins:
        return {
            'routes': [],
            'total_distance_km': 0,
            'total_trips': 0,
            'bins_collected': 0,
            'waste_collected_kg': 0
        }
    
    # Sort bins by fill percentage (collect fullest first)
    sorted_bins = sorted(bins, key=lambda b: b.fill_percentage, reverse=True)
    
    routes = []
    current_trip_bins = []
    current_trip_weight = 0
    
    for bin in sorted_bins:
        bin_weight = bin.current_fill_kg
        
        # Check if adding this bin exceeds truck capacity
        if current_trip_weight + bin_weight > truck_capacity_kg and current_trip_bins:
            # Complete current trip
            route, distance = nearest_neighbor_tsp(current_trip_bins, depot)
            routes.append({
                'trip_number': len(routes) + 1,
                'bins': route,
                'distance_km': round(distance, 2),
                'weight_kg': round(current_trip_weight, 2),
                'bin_count': len(route)
            })
            
            # Start new trip
            current_trip_bins = [bin]
            current_trip_weight = bin_weight
        else:
            current_trip_bins.append(bin)
            current_trip_weight += bin_weight
    
    # Add final trip if there are remaining bins
    if current_trip_bins:
        route, distance = nearest_neighbor_tsp(current_trip_bins, depot)
        routes.append({
            'trip_number': len(routes) + 1,
            'bins': route,
            'distance_km': round(distance, 2),
            'weight_kg': round(current_trip_weight, 2),
            'bin_count': len(route)
        })
    
    # Calculate totals
    total_distance = sum(r['distance_km'] for r in routes)
    total_weight = sum(r['weight_kg'] for r in routes)
    total_bins = sum(r['bin_count'] for r in routes)
    
    return {
        'routes': routes,
        'total_distance_km': round(total_distance, 2),
        'total_trips': len(routes),
        'bins_collected': total_bins,
        'waste_collected_kg': round(total_weight, 2),
        'avg_distance_per_trip_km': round(total_distance / len(routes), 2) if routes else 0
    }


def calculate_route_cost(route_info: Dict, config: Dict) -> Dict:
    """
    Calculate cost of collection route
    
    Args:
        route_info: Route information from optimize_collection_route
        config: Configuration dictionary with cost parameters
        
    Returns:
        Dictionary with cost breakdown
    """
    fuel_cost_per_km = config.get('costs', {}).get('fuel_cost_per_km', 2.5)
    labor_cost_per_hour = config.get('costs', {}).get('labor_cost_per_hour', 15)
    time_per_trip_hr = config.get('collection', {}).get('time_per_trip_hr', 0.85)
    
    total_distance = route_info['total_distance_km']
    total_trips = route_info['total_trips']
    
    fuel_cost = total_distance * fuel_cost_per_km
    labor_cost = total_trips * time_per_trip_hr * labor_cost_per_hour
    total_cost = fuel_cost + labor_cost
    
    return {
        'fuel_cost': round(fuel_cost, 2),
        'labor_cost': round(labor_cost, 2),
        'total_cost': round(total_cost, 2),
        'cost_per_kg': round(total_cost / route_info['waste_collected_kg'], 2) if route_info['waste_collected_kg'] > 0 else 0
    }


def calculate_environmental_impact(route_info: Dict, config: Dict) -> Dict:
    """
    Calculate environmental impact of collection route
    
    Args:
        route_info: Route information
        config: Configuration dictionary
        
    Returns:
        Dictionary with environmental metrics
    """
    carbon_per_km = config.get('sustainability', {}).get('carbon_factor_transport_kg_co2_per_km', 0.2)
    
    total_distance = route_info['total_distance_km']
    co2_emissions = total_distance * carbon_per_km
    
    return {
        'co2_emissions_kg': round(co2_emissions, 2),
        'distance_km': total_distance,
        'trips': route_info['total_trips']
    }


# Made with Bob