# 🌱 EcoSort AI - Smart Waste Management System

## PS-4: Smart Waste Management for Sustainable Campuses

A comprehensive waste management system that optimizes waste collection, promotes recycling, and contributes to a cleaner and greener campus environment.

---

## ✅ **PS-4 Requirements - FULLY IMPLEMENTED**

### 1. ✅ **Bin Status Monitoring**
- **Real-time monitoring** of 35 smart bins across 3 campus zones
- **Fill level tracking** with percentage and weight
- **Status indicators**: Critical (>90%), Warning (75-90%), Partial (50-75%), Empty (<50%)
- **Time predictions**: Estimated time until bin is full
- **Zone-wise monitoring**: Academic, Dorm, and Cafeteria zones

### 2. ✅ **Collection Alerts**
- **Automated alerts** when bins reach critical levels
- **Real-time notifications** for bins needing immediate attention
- **Alert history** and tracking
- **Priority-based alerts**: Critical, Warning, and Info levels
- **Time-based alerts**: Shows time since last collection

### 3. ✅ **Route Optimization**
- **TSP Algorithm**: Nearest Neighbor heuristic for route optimization
- **Multi-trip planning**: Considers truck capacity (2100 kg)
- **Distance calculation**: Haversine formula for GPS coordinates
- **Cost analysis**: Fuel and labor cost calculations
- **Environmental impact**: CO₂ emissions tracking
- **Route visualization**: Shows optimized collection routes

### 4. ✅ **Sustainability Dashboard**
- **Real-time metrics**: Waste collected, recycled, CO₂ reduced
- **Historical data analysis**: Trends and patterns
- **Recycling rate tracking**: Current rate and improvements
- **Environmental impact**: Trees saved, energy saved
- **Zone-wise statistics**: Performance by campus area
- **Interactive charts**: Pie charts, bar charts, line graphs

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11+
- Virtual environment (AIsus)

### **Installation**
```bash
cd "AI sustainability internship"
.\AIsus\Scripts\activate
pip install -r requirements.txt
```

### **Run the Application**
```bash
.\AIsus\Scripts\python.exe -m streamlit run ecosort_app_enhanced.py
```

### **Access the Dashboard**
Open your browser and go to: **http://localhost:8501**

---

## 📁 **Project Structure**

```
AI sustainability internship/
├── ecosort_app_enhanced.py      # Main application (ENHANCED VERSION)
├── ecosort_app.py                # Original simple version
├── config.json                   # System configuration
├── PS4_FEATURE_ANALYSIS.md       # Feature analysis document
├── README.md                     # This file
│
├── modules/                      # Backend modules
│   ├── bin_monitor.py            # Bin tracking and monitoring
│   ├── data_loader.py            # Historical data processing
│   ├── route_optimizer.py        # Route optimization (TSP)
│   ├── analytics.py              # Analytics functions
│   └── alert_system.py           # Alert management
│
├── data/                         # Data files
│   └── UoS_Waste_Optimization_RawData.csv.xls
│
├── utils/                        # Utility functions
│   └── helpers.py
│
└── AIsus/                        # Virtual environment
```

---

## 🎯 **Key Features**

### **1. Login System**
- Email/password authentication
- Quick login options (Student, Admin, Staff)
- Role-based access control
- Real-time statistics on login page

### **2. Main Dashboard**
- **5 Key Metrics Cards**:
  - Current waste in bins
  - Recyclable waste
  - CO₂ emissions reduced
  - Active smart bins
  - Recycling rate

- **Campus Bin Overview**:
  - Interactive map with bin locations
  - Real-time fill status
  - Color-coded indicators
  - Custom campus image upload support

- **Analytics Charts**:
  - Waste category breakdown (pie chart)
  - Fill level trends by zone (bar chart)
  - Historical trends (line chart)

- **Recent Alerts Panel**:
  - Critical bins (>90% full)
  - Warning bins (75-90% full)
  - Time since last collection

- **Sustainability Impact**:
  - Trees saved equivalent
  - Energy saved (kWh)
  - Monthly impact tracking

### **3. Route Optimization Page**
- **Automatic route planning** for bins needing collection
- **Multi-trip optimization** based on truck capacity
- **Cost breakdown**:
  - Fuel costs
  - Labor costs
  - Total collection cost
  - Cost per kg

- **Environmental metrics**:
  - CO₂ emissions per trip
  - Total distance traveled
  - Number of trips required

- **Route details**:
  - Bin sequence for each trip
  - Weight collected per trip
  - Distance per trip

### **4. Campus Map Upload**
- **Upload custom campus images** (PNG, JPG, JPEG)
- **Replace default map** with your actual campus layout
- **Persistent storage** across sessions
- **Easy map management** (upload/clear)

### **5. Smart Bins Page**
- **Detailed bin information** for all 35 bins
- **Filter options**:
  - By zone (Academic, Dorm, Cafeteria)
  - By type (General, Recyclable)
  - By status (Critical, Warning, Partial, Empty)

- **Bin details**:
  - Fill percentage with progress bar
  - Current weight / capacity
  - Status indicator
  - Estimated time to full

---

## 🔧 **Configuration**

Edit `config.json` to customize:

```json
{
  "bins": {
    "total_count": 35,
    "default_capacity_kg": 100
  },
  "alerts": {
    "thresholds": {
      "critical": 90,
      "warning": 75
    }
  },
  "collection": {
    "truck_capacity_kg": 2100,
    "time_per_trip_hr": 0.85
  },
  "costs": {
    "fuel_cost_per_km": 2.5,
    "labor_cost_per_hour": 15
  }
}
```

---

## 📊 **Data Flow**

1. **Historical Data** → `data_loader.py` → Zone statistics
2. **Zone Statistics** → `bin_monitor.py` → Initialize 35 bins
3. **Bin Data** → `ecosort_app_enhanced.py` → Real-time dashboard
4. **Critical Bins** → `route_optimizer.py` → Optimized routes
5. **Route Data** → Dashboard → Cost & environmental analysis

---

## 🎨 **User Interface**

### **Navigation Menu**
- 📊 Dashboard (Main overview)
- 🗑️ Smart Bins (Detailed bin list)
- 🚛 Route Optimization (Collection planning)
- 📈 Waste Analytics (Coming soon)
- 🔔 Alerts (Alert management)
- 🗺️ Campus Map (Image upload)
- ⚙️ Settings (Configuration)

### **Color Scheme**
- **Primary**: Green (#2E7D32) - Sustainability
- **Secondary**: Blue (#1976D2) - Technology
- **Warning**: Orange (#F57C00) - Attention needed
- **Critical**: Red (#D32F2F) - Urgent action
- **Success**: Light Green (#66BB6A) - Positive impact

---

## 🔄 **Real-Time Updates**

- **Auto-refresh**: Every 30 seconds
- **Bin fill simulation**: Continuous fill level updates
- **Dynamic alerts**: Real-time alert generation
- **Live statistics**: Updated metrics on every page load

---

## 📈 **Backend Modules**

### **bin_monitor.py**
- `Bin` class with properties and methods
- `initialize_bins()` - Create 35 bins from historical data
- `simulate_real_time_fill()` - Update fill levels
- `get_critical_bins()` - Find bins needing collection
- `get_zone_summary()` - Zone-wise statistics

### **data_loader.py**
- `load_waste_data()` - Load CSV/Excel data
- `get_zone_statistics()` - Calculate zone metrics
- `get_summary_statistics()` - Overall statistics
- `validate_data()` - Data validation

### **route_optimizer.py**
- `calculate_distance()` - Haversine formula
- `nearest_neighbor_tsp()` - TSP algorithm
- `optimize_collection_route()` - Multi-trip planning
- `calculate_route_cost()` - Cost analysis
- `calculate_environmental_impact()` - CO₂ tracking

---

## 🌍 **Environmental Impact**

### **Calculations**
- **Trees Saved**: 1 tree per 60 kg recycled
- **Energy Saved**: 12 kWh per kg recycled
- **CO₂ Reduced**: 0.5 kg CO₂ per kg diverted from landfill
- **CO₂ from Transport**: 0.2 kg CO₂ per km traveled

---

## 🎓 **Educational Value**

This project demonstrates:
- **IoT Integration**: Smart bin monitoring
- **Optimization Algorithms**: TSP for route planning
- **Data Analytics**: Historical data analysis
- **Sustainability Metrics**: Environmental impact tracking
- **Full-Stack Development**: Frontend + Backend integration
- **Real-Time Systems**: Live monitoring and updates

---

## 🚀 **Future Enhancements**

1. **Database Integration**: PostgreSQL/MongoDB for persistence
2. **Mobile App**: React Native or Flutter
3. **Machine Learning**: Predict waste generation patterns
4. **IoT Sensors**: Real hardware integration
5. **Email/SMS Alerts**: Notification system
6. **User Management**: Multi-user support with permissions
7. **Reporting**: PDF/Excel report generation
8. **API Development**: REST API for third-party integration

---

## 📝 **License**

This project is developed for educational purposes as part of the AI Sustainability Internship.

---

## 👥 **Team**

**Team EcoAI Nexus**
- Smart Waste Management System
- Supporting Viksit Bharat 2047 🇮🇳

---

## 📞 **Support**

For issues or questions:
1. Check `PS4_FEATURE_ANALYSIS.md` for detailed feature documentation
2. Review `config.json` for configuration options
3. Examine backend modules in `modules/` directory

---

## ✅ **Verification Checklist**

- [x] Bin status monitoring (35 bins, 3 zones)
- [x] Collection alerts (Critical, Warning, Info)
- [x] Route optimization (TSP algorithm)
- [x] Sustainability dashboard (Real-time metrics)
- [x] Image upload (Custom campus maps)
- [x] Real-time updates (Auto-refresh)
- [x] Cost analysis (Fuel + Labor)
- [x] Environmental impact (CO₂, Trees, Energy)
- [x] Historical data integration
- [x] Interactive visualizations

---

**🌱 Building a Sustainable Future, One Bin at a Time! ♻️**
