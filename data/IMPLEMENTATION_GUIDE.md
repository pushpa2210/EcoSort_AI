# 🚀 Implementation Guide - Smart Waste Management System

## Step-by-Step Implementation Instructions

---

## Phase 1: Project Cleanup

### Step 1.1: Backup Current Project
```bash
# Create backup before making changes
cp -r "AI sustainability internship" "AI sustainability internship_backup"
```

### Step 1.2: Delete Obsolete Files

**Files to Delete:**
```bash
# RAG/AI Components
rm app.py
rm rag.py
rm rag_granite.py
rm granite_test.py
rm pdf_loader.py
rm chunking.py
rm embeddings.py
rm retrieval.py

# PDF Documents (no longer needed)
rm data/BMW_Rules.pdf
rm data/Clarification_reg_booking.pdf
rm data/Ewaste_Rules.pdf
rm data/PWM_Rules.pdf.pdf
rm data/SBM(G)_Guidelines.pdf
rm "data/SBMG Phase-II Operational Guidelines.pdf"
rm data/SBMG-IEC-Guidelines.pdf
rm data/solid-waste-management-rules-2026.pdf
rm "data/Waste Segregation Poster - English.pdf"

# Vector Database
rm -rf faiss_db/

# Other files
rm "Screenshot 2026-06-01 181342.png"
rm 1M1B_guieded_course.docx
```

**Files to Keep:**
- ✅ `data/UoS_Waste_Optimization_RawData.csv.xls` (Essential!)
- ✅ `requirements.txt` (Will be updated)
- ✅ `AIsus/` (Virtual environment)

---

## Phase 2: Create New Project Structure

### Step 2.1: Create Directory Structure
```bash
# Create new directories
mkdir modules
mkdir pages
mkdir utils
mkdir assets
mkdir exports

# Create __init__.py files
touch modules/__init__.py
touch utils/__init__.py
```

### Step 2.2: Create Placeholder Files
```bash
# Module files
touch modules/data_loader.py
touch modules/bin_monitor.py
touch modules/alert_system.py
touch modules/route_optimizer.py
touch modules/analytics.py

# Utility files
touch utils/visualizations.py
touch utils/helpers.py

# Page files
touch pages/1_🗑️_Bin_Monitor.py
touch pages/2_🔔_Alerts.py
touch pages/3_🚛_Route_Optimizer.py
touch pages/4_📊_Analytics.py

# Configuration and main app
touch config.json
touch app.py
```

---

## Phase 3: Implement Core Modules

### Step 3.1: Data Loader Module

**File: `modules/data_loader.py`**

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

def load_waste_data(filepath: str = "data/UoS_Waste_Optimization_RawData.csv.xls") -> pd.DataFrame:
    """
    Load waste data from CSV file
    """
    try:
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def get_zone_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate statistics per zone
    """
    stats = {}
    for zone in df['zone'].unique():
        zone_data = df[df['zone'] == zone]
        stats[zone] = {
            'avg_waste_kg': zone_data['waste_generated_kg'].mean(),
            'avg_recyclable_kg': zone_data['recyclable_kg'].mean(),
            'avg_recyclable_fraction': zone_data['recyclable_fraction'].mean(),
            'total_waste_kg': zone_data['waste_generated_kg'].sum(),
            'avg_capture_per_bin_kg': zone_data['capture_per_bin_kg'].mean()
        }
    return stats

def calculate_fill_rate(zone: str, df: pd.DataFrame) -> float:
    """
    Calculate average fill rate (kg/hour) for a zone
    Assumes 24-hour collection cycle
    """
    zone_data = df[df['zone'] == zone]
    avg_daily_waste = zone_data['waste_generated_kg'].mean()
    # Distribute over 24 hours
    fill_rate = avg_daily_waste / 24.0
    return fill_rate

def get_date_range_data(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter data by date range
    """
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    return df[mask]

def aggregate_by_zone(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate data by zone
    """
    return df.groupby('zone').agg({
        'waste_generated_kg': 'sum',
        'recyclable_kg': 'sum',
        'recyclable_fraction': 'mean'
    }).reset_index()

# Example usage
if __name__ == "__main__":
    df = load_waste_data()
    print(f"Loaded {len(df)} records")
    
    stats = get_zone_statistics(df)
    for zone, data in stats.items():
        print(f"\n{zone}:")
        print(f"  Avg Waste: {data['avg_waste_kg']:.2f} kg/day")
        print(f"  Avg Recyclable: {data['avg_recyclable_kg']:.2f} kg/day")
```

### Step 3.2: Bin Monitor Module

**File: `modules/bin_monitor.py`**

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict
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
    last_collection: datetime = None
    fill_rate_kg_per_hour: float = 0.0
    
    def __post_init__(self):
        if self.last_collection is None:
            self.last_collection = datetime.now()
    
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
            'last_collection': self.last_collection.strftime('%Y-%m-%d %H:%M')
        }

def generate_bin_locations() -> Dict[str, Dict[str, float]]:
    """
    Generate sample GPS coordinates for bins
    Using approximate coordinates around a university campus
    """
    base_lat = 12.9716
    base_lon = 77.5946
    
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
    """
    bins = []
    locations = generate_bin_locations()
    
    # Academic zone
    for i in range(1, 11):  # 10 general bins
        bin_id = f"A-{i:02d}"
        bins.append(Bin(
            bin_id=bin_id,
            zone="Academic",
            location=locations[bin_id],
            capacity_kg=config['bins']['default_capacity_kg'],
            bin_type="General",
            fill_rate_kg_per_hour=zone_stats['Academic']['avg_waste_kg'] / 24 / 10
        ))
    
    for i in range(11, 16):  # 5 recyclable bins
        bin_id = f"A-{i:02d}"
        bins.append(Bin(
            bin_id=bin_id,
            zone="Academic",
            location=locations[bin_id],
            capacity_kg=config['bins']['default_capacity_kg'],
            bin_type="Recyclable",
            fill_rate_kg_per_hour=zone_stats['Academic']['avg_recyclable_kg'] / 24 / 5
        ))
    
    # Dorm zone
    for i in range(1, 9):  # 8 general bins
        bin_id = f"D-{i:02d}"
        bins.append(Bin(
            bin_id=bin_id,
            zone="Dorm",
            location=locations[bin_id],
            capacity_kg=config['bins']['default_capacity_kg'],
            bin_type="General",
            fill_rate_kg_per_hour=zone_stats['Dorm']['avg_waste_kg'] / 24 / 8
        ))
    
    for i in range(9, 13):  # 4 recyclable bins
        bin_id = f"D-{i:02d}"
        bins.append(Bin(
            bin_id=bin_id,
            zone="Dorm",
            location=locations[bin_id],
            capacity_kg=config['bins']['default_capacity_kg'],
            bin_type="Recyclable",
            fill_rate_kg_per_hour=zone_stats['Dorm']['avg_recyclable_kg'] / 24 / 4
        ))
    
    # Cafeteria zone
    for i in range(1, 6):  # 5 general bins
        bin_id = f"C-{i:02d}"
        bins.append(Bin(
            bin_id=bin_id,
            zone="Cafeteria",
            location=locations[bin_id],
            capacity_kg=config['bins']['default_capacity_kg'],
            bin_type="General",
            fill_rate_kg_per_hour=zone_stats['Cafeteria']['avg_waste_kg'] / 24 / 5
        ))
    
    for i in range(6, 9):  # 3 recyclable bins
        bin_id = f"C-{i:02d}"
        bins.append(Bin(
            bin_id=bin_id,
            zone="Cafeteria",
            location=locations[bin_id],
            capacity_kg=config['bins']['default_capacity_kg'],
            bin_type="Recyclable",
            fill_rate_kg_per_hour=zone_stats['Cafeteria']['avg_recyclable_kg'] / 24 / 3
        ))
    
    return bins

def simulate_real_time_fill(bins: List[Bin], last_update: datetime):
    """
    Update all bin fill levels based on time elapsed
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

def get_critical_bins(bins: List[Bin]) -> List[Bin]:
    """Get bins requiring immediate attention"""
    return [bin for bin in bins if bin.fill_percentage >= 90]
```

---

## Phase 4: Configuration Setup

### Step 4.1: Create Configuration File

**File: `config.json`**

```json
{
  "system": {
    "name": "Smart Waste Management System",
    "version": "1.0.0",
    "campus_name": "University Campus",
    "campus_location": {
      "lat": 12.9716,
      "lon": 77.5946
    }
  },
  "bins": {
    "total_count": 35,
    "zones": {
      "Academic": {
        "general": 10,
        "recyclable": 5
      },
      "Dorm": {
        "general": 8,
        "recyclable": 4
      },
      "Cafeteria": {
        "general": 5,
        "recyclable": 3
      }
    },
    "default_capacity_kg": 100
  },
  "alerts": {
    "thresholds": {
      "critical": 90,
      "warning": 75,
      "info": 50
    },
    "auto_refresh_seconds": 30,
    "max_alerts_display": 20
  },
  "collection": {
    "truck_capacity_kg": 2100,
    "time_per_trip_hr": 0.85,
    "labor_hours_per_trip": 2,
    "trip_cost": 100,
    "time_available_hr": 10,
    "labor_available_hr": 14,
    "budget": 1800,
    "depot_location": {
      "lat": 12.9716,
      "lon": 77.5946
    }
  },
  "costs": {
    "recycling_cost_per_kg": 0.10,
    "landfill_cost_per_kg": 0.08,
    "fuel_cost_per_km": 2.5,
    "labor_cost_per_hour": 15,
    "bin_maintenance_cost": 0.92
  },
  "sustainability": {
    "recycling_target_frac": 0.55,
    "carbon_factor_landfill_kg_co2_per_kg": 0.5,
    "carbon_factor_recycling_saved_kg_co2_per_kg": 0.3,
    "carbon_factor_transport_kg_co2_per_km": 0.2
  },
  "simulation": {
    "start_date": "2025-01-01",
    "simulation_speed_multiplier": 1.0,
    "random_seed": 42,
    "initial_fill_percentage_range": [10, 40]
  },
  "ui": {
    "theme": "light",
    "primary_color": "#2E7D32",
    "secondary_color": "#1976D2",
    "warning_color": "#F57C00",
    "danger_color": "#D32F2F",
    "success_color": "#66BB6A",
    "chart_height": 400,
    "map_zoom": 15,
    "page_icon": "🌍"
  }
}
```

---

## Phase 5: Update Dependencies

### Step 5.1: Create New requirements.txt

**File: `requirements.txt`**

```txt
# Core Framework
streamlit==1.58.0

# Data Processing
pandas==3.0.3
numpy==2.4.6

# Visualization
plotly==5.24.1
folium==0.18.0

# Optimization
scipy==1.17.1

# Utilities
python-dateutil==2.9.0.post0
streamlit-autorefresh==1.0.1

# Optional: For advanced features
openpyxl==3.1.5  # For Excel file support
```

### Step 5.2: Install Dependencies
```bash
# Activate virtual environment
cd "AI sustainability internship"
.\AIsus\Scripts\activate

# Install new dependencies
pip install -r requirements.txt

# Uninstall old dependencies (optional)
pip uninstall sentence-transformers faiss-cpu transformers torch accelerate langchain PyPDF2 -y
```

---

## Phase 6: Quick Start Guide

### Step 6.1: Verify Setup
```bash
# Check Python version
python --version  # Should be 3.11+

# Check Streamlit installation
streamlit --version

# List installed packages
pip list
```

### Step 6.2: Run Application
```bash
# Navigate to project directory
cd "AI sustainability internship"

# Run Streamlit app
streamlit run app.py
```

### Step 6.3: Access Dashboard
- Open browser to: `http://localhost:8501`
- Dashboard should load with all features

---

## Phase 7: Testing Checklist

### Functional Testing
- [ ] Dashboard loads without errors
- [ ] Bin status displays correctly
- [ ] Alerts generate when thresholds exceeded
- [ ] Route optimization calculates paths
- [ ] Analytics charts render properly
- [ ] Data exports work correctly

### Performance Testing
- [ ] Page load time < 3 seconds
- [ ] Auto-refresh works smoothly
- [ ] No memory leaks after extended use
- [ ] Charts render quickly

### User Experience Testing
- [ ] Navigation is intuitive
- [ ] Colors and themes are consistent
- [ ] Mobile responsive (if applicable)
- [ ] Error messages are clear

---

## Phase 8: Troubleshooting

### Common Issues

**Issue 1: Module Import Errors**
```python
# Solution: Add to app.py
import sys
sys.path.append('.')
```

**Issue 2: Data File Not Found**
```python
# Solution: Use absolute path
import os
data_path = os.path.join(os.path.dirname(__file__), 'data', 'UoS_Waste_Optimization_RawData.csv.xls')
```

**Issue 3: Streamlit Caching Issues**
```bash
# Clear cache
streamlit cache clear
```

**Issue 4: Port Already in Use**
```bash
# Use different port
streamlit run app.py --server.port 8502
```

---

## Phase 9: Deployment Options

### Option 1: Streamlit Cloud (Recommended)
```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# 2. Deploy on Streamlit Cloud
# - Go to share.streamlit.io
# - Connect GitHub repo
# - Deploy
```

### Option 2: Local Network
```bash
# Run on local network
streamlit run app.py --server.address 0.0.0.0
```

### Option 3: Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

---

## Phase 10: Next Steps

### Immediate Tasks
1. ✅ Complete all module implementations
2. ✅ Test each feature thoroughly
3. ✅ Write user documentation
4. ✅ Create demo video/screenshots

### Future Enhancements
1. 🔮 Add real IoT sensor integration
2. 🔮 Implement user authentication
3. 🔮 Add email/SMS notifications
4. 🔮 Create mobile app
5. 🔮 Add predictive analytics with ML

---

## Code Quality Guidelines

### Python Style
- Follow PEP 8 conventions
- Use type hints
- Write docstrings for all functions
- Keep functions small and focused

### Streamlit Best Practices
- Use `st.cache_data` for data loading
- Use `st.cache_resource` for model loading
- Implement proper error handling
- Use session state for persistence

### Git Workflow
```bash
# Feature branch workflow
git checkout -b feature/bin-monitor
# Make changes
git add .
git commit -m "Add bin monitoring feature"
git push origin feature/bin-monitor
# Create pull request
```

---

## Resources

### Documentation
- [Streamlit Docs](https://docs.streamlit.io)
- [Plotly Docs](https://plotly.com/python/)
- [Pandas Docs](https://pandas.pydata.org/docs/)

### Tutorials
- Streamlit Gallery: https://streamlit.io/gallery
- Plotly Examples: https://plotly.com/python/
- Folium Maps: https://python-visualization.github.io/folium/

### Community
- Streamlit Forum: https://discuss.streamlit.io
- Stack Overflow: Tag `streamlit`

---

This implementation guide provides step-by-step instructions for transforming your project. Follow each phase sequentially for best results!