"""
Analytics Module - Calculate sustainability metrics and generate insights
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from modules.bin_monitor import Bin


def calculate_daily_metrics(df: pd.DataFrame, date: str) -> Dict:
    """
    Calculate metrics for a specific date
    
    Args:
        df: DataFrame with waste data
        date: Date string (YYYY-MM-DD)
        
    Returns:
        Dictionary with daily metrics
    """
    if df.empty or 'date' not in df.columns:
        return {}
    
    day_data = df[df['date'] == date]
    
    if day_data.empty:
        return {}
    
    total_waste = day_data['waste_generated_kg'].sum() if 'waste_generated_kg' in df.columns else 0
    recyclable = day_data['recyclable_kg'].sum() if 'recyclable_kg' in df.columns else 0
    
    return {
        'date': date,
        'total_waste_kg': total_waste,
        'recyclable_kg': recyclable,
        'recycling_rate': (recyclable / total_waste * 100) if total_waste > 0 else 0,
        'cost_per_kg': day_data['landfill_cost_per_kg'].mean() if 'landfill_cost_per_kg' in df.columns else 0,
        'num_collections': len(day_data)
    }


def calculate_zone_comparison(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Compare waste generation across zones for date range
    
    Args:
        df: DataFrame with waste data
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        DataFrame with zone comparison
    """
    if df.empty or 'zone' not in df.columns:
        return pd.DataFrame()
    
    # Filter by date range
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df[mask]
    
    if filtered_df.empty:
        return pd.DataFrame()
    
    # Group by zone
    zone_data = filtered_df.groupby('zone').agg({
        'waste_generated_kg': 'sum',
        'recyclable_kg': 'sum',
        'recyclable_fraction': 'mean'
    }).reset_index()
    
    # Calculate recycling rate
    zone_data['recycling_rate'] = (zone_data['recyclable_kg'] / zone_data['waste_generated_kg'] * 100)
    
    return zone_data


def calculate_recycling_performance(df: pd.DataFrame, target: float) -> Dict:
    """
    Compare actual recycling rate vs target
    
    Args:
        df: DataFrame with waste data
        target: Target recycling rate (0-1)
        
    Returns:
        Dictionary with performance metrics
    """
    if df.empty or 'recyclable_fraction' not in df.columns:
        return {}
    
    current_rate = df['recyclable_fraction'].mean()
    gap = current_rate - target
    
    return {
        'current_rate': current_rate * 100,
        'target_rate': target * 100,
        'gap': gap * 100,
        'status': 'Above Target' if gap >= 0 else 'Below Target',
        'performance_pct': (current_rate / target * 100) if target > 0 else 0
    }


def calculate_cost_breakdown(df: pd.DataFrame, date_range: Optional[Tuple[str, str]] = None) -> Dict:
    """
    Break down costs by category
    
    Args:
        df: DataFrame with waste data
        date_range: Optional tuple of (start_date, end_date)
        
    Returns:
        Dictionary with cost breakdown
    """
    if df.empty:
        return {}
    
    # Filter by date range if provided
    if date_range:
        mask = (df['date'] >= date_range[0]) & (df['date'] <= date_range[1])
        filtered = df[mask]
        assert isinstance(filtered, pd.DataFrame)
        df = filtered
    
    if df.empty:
        return {}
    
    # Calculate costs
    total_waste = df['waste_generated_kg'].sum() if 'waste_generated_kg' in df.columns else 0
    recyclable = df['recyclable_kg'].sum() if 'recyclable_kg' in df.columns else 0
    landfill = total_waste - recyclable
    
    recycling_cost_per_kg = df['recycling_cost_per_kg'].mean() if 'recycling_cost_per_kg' in df.columns else 0.10
    landfill_cost_per_kg = df['landfill_cost_per_kg'].mean() if 'landfill_cost_per_kg' in df.columns else 0.08
    trip_cost = df['trip_cost'].mean() if 'trip_cost' in df.columns else 100
    
    collection_costs = len(df) * trip_cost
    recycling_costs = recyclable * recycling_cost_per_kg
    landfill_costs = landfill * landfill_cost_per_kg
    total_costs = collection_costs + recycling_costs + landfill_costs
    
    return {
        'collection_costs': collection_costs,
        'recycling_costs': recycling_costs,
        'landfill_costs': landfill_costs,
        'total_costs': total_costs,
        'cost_per_kg': total_costs / total_waste if total_waste > 0 else 0,
        'breakdown_pct': {
            'collection': (collection_costs / total_costs * 100) if total_costs > 0 else 0,
            'recycling': (recycling_costs / total_costs * 100) if total_costs > 0 else 0,
            'landfill': (landfill_costs / total_costs * 100) if total_costs > 0 else 0
        }
    }


def calculate_carbon_footprint(df: pd.DataFrame, config: Dict, date_range: Optional[Tuple[str, str]] = None) -> Dict:
    """
    Estimate carbon emissions
    
    Args:
        df: DataFrame with waste data
        config: Configuration dictionary with carbon factors
        date_range: Optional tuple of (start_date, end_date)
        
    Returns:
        Dictionary with carbon footprint metrics
    """
    if df.empty:
        return {}
    
    # Filter by date range if provided
    if date_range:
        mask = (df['date'] >= date_range[0]) & (df['date'] <= date_range[1])
        filtered = df[mask]
        assert isinstance(filtered, pd.DataFrame)
        df = filtered
    
    if df.empty:
        return {}
    
    # Get carbon factors from config
    sustainability = config.get('sustainability', {})
    landfill_factor = sustainability.get('carbon_factor_landfill_kg_co2_per_kg', 0.5)
    recycling_saved_factor = sustainability.get('carbon_factor_recycling_saved_kg_co2_per_kg', 0.3)
    transport_factor = sustainability.get('carbon_factor_transport_kg_co2_per_km', 0.2)
    
    # Calculate waste amounts
    total_waste = df['waste_generated_kg'].sum() if 'waste_generated_kg' in df.columns else 0
    recyclable = df['recyclable_kg'].sum() if 'recyclable_kg' in df.columns else 0
    landfill = total_waste - recyclable
    
    # Calculate emissions
    landfill_emissions = landfill * landfill_factor
    recycling_savings = recyclable * recycling_saved_factor
    
    # Estimate transport emissions (assume 10 km average per trip)
    num_trips = len(df)
    transport_emissions = num_trips * 10 * transport_factor
    
    net_emissions = landfill_emissions + transport_emissions - recycling_savings
    
    return {
        'landfill_emissions_kg_co2': landfill_emissions,
        'transport_emissions_kg_co2': transport_emissions,
        'recycling_savings_kg_co2': recycling_savings,
        'net_emissions_kg_co2': net_emissions,
        'emissions_per_kg_waste': net_emissions / total_waste if total_waste > 0 else 0
    }


def generate_waste_forecast(df: pd.DataFrame, days_ahead: int = 7) -> pd.DataFrame:
    """
    Simple moving average forecast for waste generation
    
    Args:
        df: DataFrame with waste data
        days_ahead: Number of days to forecast
        
    Returns:
        DataFrame with predicted waste
    """
    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()
    
    # Calculate daily totals
    grouped_sum = df.groupby('date')['waste_generated_kg'].sum()
    assert isinstance(grouped_sum, pd.Series)
    daily_data = grouped_sum.reset_index()
    daily_data = daily_data.sort_values('date')
    
    # Calculate moving average (7-day window)
    window = min(7, len(daily_data))
    avg_waste = daily_data['waste_generated_kg'].tail(window).mean()
    
    # Generate forecast dates
    last_date = daily_data['date'].max()
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead)
    
    # Create forecast dataframe
    forecast_df = pd.DataFrame({
        'date': forecast_dates,
        'predicted_waste_kg': [avg_waste] * days_ahead,
        'confidence': ['Medium'] * days_ahead
    })
    
    return forecast_df


def calculate_bin_utilization(bins: List[Bin], historical_data: Optional[pd.DataFrame] = None) -> Dict:
    """
    Calculate bin usage patterns
    
    Args:
        bins: List of Bin objects
        historical_data: Optional historical data
        
    Returns:
        Dictionary with utilization metrics
    """
    if not bins:
        return {}
    
    total_capacity = sum(b.capacity_kg for b in bins)
    total_fill = sum(b.current_fill_kg for b in bins)
    avg_utilization = (total_fill / total_capacity * 100) if total_capacity > 0 else 0
    
    # Identify underutilized bins (< 30% average fill)
    underutilized = [b for b in bins if b.fill_percentage < 30]
    
    # Identify overutilized bins (> 80% average fill)
    overutilized = [b for b in bins if b.fill_percentage > 80]
    
    # Calculate by zone
    zones = set(b.zone for b in bins)
    zone_utilization = {}
    
    for zone in zones:
        zone_bins = [b for b in bins if b.zone == zone]
        zone_capacity = sum(b.capacity_kg for b in zone_bins)
        zone_fill = sum(b.current_fill_kg for b in zone_bins)
        zone_utilization[zone] = (zone_fill / zone_capacity * 100) if zone_capacity > 0 else 0
    
    return {
        'overall_utilization_pct': avg_utilization,
        'total_capacity_kg': total_capacity,
        'total_fill_kg': total_fill,
        'underutilized_bins': len(underutilized),
        'overutilized_bins': len(overutilized),
        'zone_utilization': zone_utilization,
        'efficiency_score': min(100, avg_utilization * 1.2)  # Bonus for higher utilization
    }


def calculate_trend_analysis(df: pd.DataFrame, metric: str = 'waste_generated_kg') -> Dict:
    """
    Analyze trends in waste generation
    
    Args:
        df: DataFrame with waste data
        metric: Column name to analyze
        
    Returns:
        Dictionary with trend analysis
    """
    if df.empty or metric not in df.columns or 'date' not in df.columns:
        return {}
    
    # Group by date
    grouped_sum = df.groupby('date')[metric].sum()
    assert isinstance(grouped_sum, pd.Series)
    daily_data = grouped_sum.reset_index()
    daily_data = daily_data.sort_values('date')
    
    if len(daily_data) < 2:
        return {}
    
    # Calculate trend
    values = daily_data[metric].values
    values_array = np.asarray(values, dtype=np.float64)
    avg_value = np.mean(values_array)
    
    # Simple linear trend
    x = np.arange(len(values_array))
    slope = np.polyfit(x, values_array, 1)[0]
    
    # Determine trend direction
    if slope > avg_value * 0.01:  # More than 1% increase per day
        trend = "Increasing"
    elif slope < -avg_value * 0.01:  # More than 1% decrease per day
        trend = "Decreasing"
    else:
        trend = "Stable"
    
    return {
        'metric': metric,
        'average': avg_value,
        'trend': trend,
        'slope': slope,
        'min_value': np.min(values_array),
        'max_value': np.max(values_array),
        'std_dev': np.std(values_array)
    }


def calculate_efficiency_metrics(bins: List[Bin], config: Dict) -> Dict:
    """
    Calculate operational efficiency metrics
    
    Args:
        bins: List of Bin objects
        config: Configuration dictionary
        
    Returns:
        Dictionary with efficiency metrics
    """
    if not bins:
        return {}
    
    # Collection efficiency
    bins_needing_collection = len([b for b in bins if b.fill_percentage >= 75])
    total_bins = len(bins)
    collection_efficiency = (bins_needing_collection / total_bins * 100) if total_bins > 0 else 0
    
    # Capacity utilization
    total_capacity = sum(b.capacity_kg for b in bins)
    total_fill = sum(b.current_fill_kg for b in bins)
    capacity_utilization = (total_fill / total_capacity * 100) if total_capacity > 0 else 0
    
    # Route efficiency (estimated)
    zones = set(b.zone for b in bins)
    bins_per_zone = {zone: len([b for b in bins if b.zone == zone]) for zone in zones}
    avg_bins_per_zone = np.mean(list(bins_per_zone.values()))
    
    return {
        'collection_efficiency_pct': collection_efficiency,
        'capacity_utilization_pct': capacity_utilization,
        'bins_needing_collection': bins_needing_collection,
        'total_bins': total_bins,
        'avg_bins_per_zone': avg_bins_per_zone,
        'overall_efficiency_score': (collection_efficiency + capacity_utilization) / 2
    }


def generate_summary_report(df: pd.DataFrame, bins: List[Bin], config: Dict) -> Dict:
    """
    Generate comprehensive summary report
    
    Args:
        df: DataFrame with historical data
        bins: List of current Bin objects
        config: Configuration dictionary
        
    Returns:
        Dictionary with complete summary
    """
    summary = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_summary': {},
        'current_status': {},
        'performance': {},
        'sustainability': {}
    }
    
    # Data summary
    if not df.empty:
        summary['data_summary'] = {
            'total_records': len(df),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d') if 'date' in df.columns else None,
                'end': df['date'].max().strftime('%Y-%m-%d') if 'date' in df.columns else None
            },
            'total_waste_kg': df['waste_generated_kg'].sum() if 'waste_generated_kg' in df.columns else 0,
            'avg_daily_waste_kg': df['waste_generated_kg'].mean() if 'waste_generated_kg' in df.columns else 0
        }
    
    # Current status
    if bins:
        summary['current_status'] = {
            'total_bins': len(bins),
            'bins_critical': len([b for b in bins if b.status == 'Critical']),
            'bins_warning': len([b for b in bins if b.status == 'Warning']),
            'avg_fill_percentage': np.mean([b.fill_percentage for b in bins])
        }
    
    # Performance metrics
    if not df.empty:
        target = config.get('sustainability', {}).get('recycling_target_frac', 0.55)
        summary['performance'] = calculate_recycling_performance(df, target)
    
    # Sustainability metrics
    if not df.empty:
        summary['sustainability'] = calculate_carbon_footprint(df, config)
    
    return summary

# Made with Bob
