"""
Data Loader Module - Load and process historical waste data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def load_waste_data(filepath: str = "data/UoS_Waste_Optimization_RawData.csv.xls") -> pd.DataFrame:
    """
    Load waste data from CSV/Excel file
    
    Args:
        filepath: Path to the data file
        
    Returns:
        DataFrame with waste data
    """
    try:
        # Try reading as CSV first
        try:
            df = pd.read_csv(filepath)
        except:
            # If CSV fails, try Excel
            df = pd.read_excel(filepath)
        
        # Convert date column to datetime if it exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()


def get_zone_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate statistics per zone
    
    Args:
        df: DataFrame with waste data
        
    Returns:
        Dictionary with zone statistics
    """
    if df.empty:
        return {}
    
    stats = {}
    
    # Check if zone column exists
    if 'zone' not in df.columns:
        print("Warning: 'zone' column not found in data")
        return stats
    
    for zone in df['zone'].unique():
        zone_data = df[df['zone'] == zone]
        
        stats[zone] = {
            'avg_waste_kg': zone_data['waste_generated_kg'].mean() if 'waste_generated_kg' in df.columns else 0,
            'avg_recyclable_kg': zone_data['recyclable_kg'].mean() if 'recyclable_kg' in df.columns else 0,
            'avg_recyclable_fraction': zone_data['recyclable_fraction'].mean() if 'recyclable_fraction' in df.columns else 0,
            'total_waste_kg': zone_data['waste_generated_kg'].sum() if 'waste_generated_kg' in df.columns else 0,
            'avg_capture_per_bin_kg': zone_data['capture_per_bin_kg'].mean() if 'capture_per_bin_kg' in df.columns else 0,
            'record_count': len(zone_data)
        }
    
    return stats


def calculate_fill_rate(zone: str, df: pd.DataFrame, hours: int = 24) -> float:
    """
    Calculate average fill rate (kg/hour) for a zone
    
    Args:
        zone: Zone name
        df: DataFrame with waste data
        hours: Number of hours to distribute waste over (default 24)
        
    Returns:
        Fill rate in kg/hour
    """
    if df.empty or 'zone' not in df.columns:
        return 0.0
    
    zone_data = df[df['zone'] == zone]
    
    if zone_data.empty or 'waste_generated_kg' not in df.columns:
        return 0.0
    
    avg_daily_waste = zone_data['waste_generated_kg'].mean()
    fill_rate = avg_daily_waste / hours
    
    return fill_rate


def get_date_range_data(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter data by date range
    
    Args:
        df: DataFrame with waste data
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Filtered DataFrame
    """
    if df.empty or 'date' not in df.columns:
        return df
    
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    result = df[mask]
    assert isinstance(result, pd.DataFrame)
    return result


def aggregate_by_zone(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate data by zone
    
    Args:
        df: DataFrame with waste data
        
    Returns:
        Aggregated DataFrame
    """
    if df.empty or 'zone' not in df.columns:
        return pd.DataFrame()
    
    agg_dict = {}
    
    if 'waste_generated_kg' in df.columns:
        agg_dict['waste_generated_kg'] = 'sum'
    if 'recyclable_kg' in df.columns:
        agg_dict['recyclable_kg'] = 'sum'
    if 'recyclable_fraction' in df.columns:
        agg_dict['recyclable_fraction'] = 'mean'
    
    if not agg_dict:
        return pd.DataFrame()
    
    return df.groupby('zone').agg(agg_dict).reset_index()


def aggregate_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate data by date
    
    Args:
        df: DataFrame with waste data
        
    Returns:
        Aggregated DataFrame
    """
    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()
    
    agg_dict = {}
    
    if 'waste_generated_kg' in df.columns:
        agg_dict['waste_generated_kg'] = 'sum'
    if 'recyclable_kg' in df.columns:
        agg_dict['recyclable_kg'] = 'sum'
    if 'recyclable_fraction' in df.columns:
        agg_dict['recyclable_fraction'] = 'mean'
    
    if not agg_dict:
        return pd.DataFrame()
    
    return df.groupby('date').agg(agg_dict).reset_index()


def get_summary_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate overall summary statistics
    
    Args:
        df: DataFrame with waste data
        
    Returns:
        Dictionary with summary statistics
    """
    if df.empty:
        return {}
    
    stats = {
        'total_records': len(df),
        'date_range': {
            'start': df['date'].min() if 'date' in df.columns else None,
            'end': df['date'].max() if 'date' in df.columns else None
        },
        'total_waste_kg': df['waste_generated_kg'].sum() if 'waste_generated_kg' in df.columns else 0,
        'total_recyclable_kg': df['recyclable_kg'].sum() if 'recyclable_kg' in df.columns else 0,
        'avg_daily_waste_kg': df['waste_generated_kg'].mean() if 'waste_generated_kg' in df.columns else 0,
        'avg_recycling_rate': df['recyclable_fraction'].mean() if 'recyclable_fraction' in df.columns else 0,
        'zones': df['zone'].unique().tolist() if 'zone' in df.columns else []
    }
    
    return stats


def prepare_simulation_data(df: pd.DataFrame, config: Dict) -> Dict:
    """
    Prepare data for simulation
    
    Args:
        df: DataFrame with waste data
        config: Configuration dictionary
        
    Returns:
        Dictionary with simulation parameters
    """
    zone_stats = get_zone_statistics(df)
    
    simulation_data = {
        'zone_stats': zone_stats,
        'fill_rates': {},
        'bin_counts': config.get('bins', {}).get('zones', {})
    }
    
    # Calculate fill rates for each zone
    for zone in zone_stats.keys():
        simulation_data['fill_rates'][zone] = calculate_fill_rate(zone, df)
    
    return simulation_data


def validate_data(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Validate data structure and required columns
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Dictionary with validation results
    """
    required_columns = ['date', 'zone', 'waste_generated_kg', 'recyclable_kg', 'recyclable_fraction']
    
    validation = {
        'is_valid': True,
        'has_data': not df.empty,
        'missing_columns': [],
        'data_types_correct': True
    }
    
    # Check for missing columns
    for col in required_columns:
        if col not in df.columns:
            validation['missing_columns'].append(col)
            validation['is_valid'] = False
    
    # Check data types
    if 'date' in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            validation['data_types_correct'] = False
            validation['is_valid'] = False
    
    return validation


# Example usage and testing
if __name__ == "__main__":
    # Load data
    df = load_waste_data()
    
    if not df.empty:
        print(f"Loaded {len(df)} records")
        
        # Validate data
        validation = validate_data(df)
        print(f"\nData validation: {validation}")
        
        # Get summary statistics
        summary = get_summary_statistics(df)
        print(f"\nSummary Statistics:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Get zone statistics
        stats = get_zone_statistics(df)
        print(f"\nZone Statistics:")
        for zone, data in stats.items():
            print(f"\n{zone}:")
            print(f"  Avg Waste: {data['avg_waste_kg']:.2f} kg/day")
            print(f"  Avg Recyclable: {data['avg_recyclable_kg']:.2f} kg/day")
            print(f"  Recycling Rate: {data['avg_recyclable_fraction']*100:.1f}%")
    else:
        print("No data loaded")

# Made with Bob
