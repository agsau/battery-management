import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
import io
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Battery Cell Simulator",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 2rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'cells_data' not in st.session_state:
        st.session_state.cells_data = {}
    if 'tasks_data' not in st.session_state:
        st.session_state.tasks_data = {}
    if 'simulation_running' not in st.session_state:
        st.session_state.simulation_running = False
    if 'historical_data' not in st.session_state:
        st.session_state.historical_data = []
    if 'current_time' not in st.session_state:
        st.session_state.current_time = 0

initialize_session_state()

# Sidebar navigation
st.sidebar.markdown("# 🔋 Battery Simulator")
page = st.sidebar.selectbox(
    "Navigate to:",
    ["🏠 Home", "⚡ Setup Cells", "📋 Add Tasks", "📊 Real-time Analysis", "📥 Data Export"]
)

# Helper functions
def generate_cell_data(cell_type, cell_id):
    """Generate initial cell data based on type"""
    voltage = 3.2 if cell_type.lower() == "lfp" else 3.6
    min_voltage = 2.8 if cell_type.lower() == "lfp" else 3.2
    max_voltage = 3.6 if cell_type.lower() == "lfp" else 4.0
    current = round(random.uniform(0.1, 2.0), 2)
    temp = round(random.uniform(25, 40), 1)
    capacity = round(voltage * current, 2)
    
    return {
        "cell_id": f"cell_{cell_id}_{cell_type}",
        "type": cell_type,
        "voltage": voltage,
        "current": current,
        "temp": temp,
        "capacity": capacity,
        "min_voltage": min_voltage,
        "max_voltage": max_voltage,
        "status": "Active"
    }

def simulate_real_time_data():
    """Simulate real-time changes in cell data"""
    if st.session_state.cells_data:
        for cell_id, cell_data in st.session_state.cells_data.items():
            # Add small random variations
            voltage_change = random.uniform(-0.05, 0.05)
            temp_change = random.uniform(-1, 1)
            current_change = random.uniform(-0.1, 0.1)
            
            # Update with constraints
            new_voltage = max(cell_data["min_voltage"], 
                            min(cell_data["max_voltage"], 
                                cell_data["voltage"] + voltage_change))
            new_temp = max(20, min(50, cell_data["temp"] + temp_change))
            new_current = max(0, cell_data["current"] + current_change)
            
            st.session_state.cells_data[cell_id]["voltage"] = round(new_voltage, 2)
            st.session_state.cells_data[cell_id]["temp"] = round(new_temp, 1)
            st.session_state.cells_data[cell_id]["current"] = round(new_current, 2)
            st.session_state.cells_data[cell_id]["capacity"] = round(new_voltage * new_current, 2)
        
        # Store historical data
        timestamp = datetime.now() + timedelta(seconds=st.session_state.current_time)
        for cell_id, cell_data in st.session_state.cells_data.items():
            st.session_state.historical_data.append({
                "timestamp": timestamp,
                "cell_id": cell_id,
                "voltage": cell_data["voltage"],
                "current": cell_data["current"],
                "temp": cell_data["temp"],
                "capacity": cell_data["capacity"]
            })
        
        st.session_state.current_time += 1

# Page 1: Home
if page == "🏠 Home":
    st.markdown('<div class="main-header"><h1>🔋 Battery Cell Simulation Dashboard</h1><p>Advanced Battery Testing & Analysis Platform</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎯 Features
        - **Multi-cell Management**: Setup and monitor multiple battery cells
        - **Task Processing**: CC_CV, IDLE, CC_CD operations  
        - **Real-time Analytics**: Live monitoring with interactive charts
        - **Data Export**: Comprehensive CSV reporting
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Cell Types Supported
        - **LFP (Lithium Iron Phosphate)**
          - Voltage: 3.2V (2.8V - 3.6V)
          - High safety, long cycle life
        - **NMC (Nickel Manganese Cobalt)**  
          - Voltage: 3.6V (3.2V - 4.0V)
          - High energy density
        """)
    
    with col3:
        st.markdown("""
        ### 📊 Quick Stats
        """)
        if st.session_state.cells_data:
            st.metric("Active Cells", len(st.session_state.cells_data))
            st.metric("Active Tasks", len(st.session_state.tasks_data))
            avg_voltage = np.mean([cell["voltage"] for cell in st.session_state.cells_data.values()])
            st.metric("Avg Voltage", f"{avg_voltage:.2f}V")
        else:
            st.info("No cells configured yet. Go to Setup Cells to get started!")

# Page 2: Setup Cells
elif page == "⚡ Setup Cells":
    st.markdown('<div class="main-header"><h2>⚡ Battery Cell Setup</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Add New Cell")
        
        with st.form("add_cell_form"):
            cell_type = st.selectbox("Cell Type", ["LFP", "NMC"])
            cell_count = st.number_input("Number of Cells", min_value=1, max_value=20, value=1)
            
            submitted = st.form_submit_button("Add Cells", use_container_width=True)
            
            if submitted:
                start_id = len(st.session_state.cells_data) + 1
                for i in range(cell_count):
                    cell_id = f"cell_{start_id + i}_{cell_type.lower()}"
                    st.session_state.cells_data[cell_id] = generate_cell_data(cell_type.lower(), start_id + i)
                
                st.success(f"Added {cell_count} {cell_type} cell(s)!")
                st.rerun()
    
    with col2:
        st.subheader("Current Cells Configuration")
        
        if st.session_state.cells_data:
            # Create DataFrame for display
            df = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
            
            # Display interactive table
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "voltage": st.column_config.NumberColumn("Voltage (V)", format="%.2f"),
                    "current": st.column_config.NumberColumn("Current (A)", format="%.2f"),
                    "temp": st.column_config.NumberColumn("Temperature (°C)", format="%.1f"),
                    "capacity": st.column_config.NumberColumn("Capacity (Wh)", format="%.2f"),
                    "min_voltage": st.column_config.NumberColumn("Min V", format="%.1f"),
                    "max_voltage": st.column_config.NumberColumn("Max V", format="%.1f"),
                }
            )
            
            # Cell management
            st.subheader("Cell Management")
            col3, col4 = st.columns(2)
            
            with col3:
                if st.button("🔄 Refresh Cell Data", use_container_width=True):
                    simulate_real_time_data()
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Clear All Cells", use_container_width=True):
                    st.session_state.cells_data = {}
                    st.session_state.historical_data = []
                    st.success("All cells cleared!")
                    st.rerun()
        else:
            st.info("No cells configured yet. Add some cells to get started!")

# Page 3: Add Tasks  
elif page == "📋 Add Tasks":
    st.markdown('<div class="main-header"><h2>📋 Task Management</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Add New Task")
        
        with st.form("add_task_form"):
            task_type = st.selectbox("Task Type", ["CC_CV", "IDLE", "CC_CD"])
            
            task_data = {"task_type": task_type}
            
            if task_type == "CC_CV":
                st.markdown("**Constant Current - Constant Voltage**")
                cc_input = st.text_input("CC/CP Value", placeholder="e.g., 5A or 10W")
                cv_voltage = st.number_input("CV Voltage (V)", min_value=0.0, value=3.6, step=0.1)
                current = st.number_input("Current (A)", min_value=0.0, value=1.0, step=0.1)
                capacity = st.number_input("Capacity", min_value=0.0, value=10.0, step=0.1)
                time_seconds = st.number_input("Time (seconds)", min_value=1, value=3600)
                
                task_data.update({
                    "cc_cp": cc_input,
                    "cv_voltage": cv_voltage,
                    "current": current,
                    "capacity": capacity,
                    "time_seconds": time_seconds
                })
                
            elif task_type == "IDLE":
                st.markdown("**Idle State**")
                time_seconds = st.number_input("Time (seconds)", min_value=1, value=1800)
                task_data["time_seconds"] = time_seconds
                
            elif task_type == "CC_CD":
                st.markdown("**Constant Current - Constant Discharge**")
                cc_input = st.text_input("CC/CP Value", placeholder="e.g., 5A or 10W")
                voltage = st.number_input("Voltage (V)", min_value=0.0, value=3.2, step=0.1)
                capacity = st.number_input("Capacity", min_value=0.0, value=10.0, step=0.1)
                time_seconds = st.number_input("Time (seconds)", min_value=1, value=3600)
                
                task_data.update({
                    "cc_cp": cc_input,
                    "voltage": voltage,
                    "capacity": capacity,
                    "time_seconds": time_seconds
                })
            
            submitted = st.form_submit_button("Add Task", use_container_width=True)
            
            if submitted:
                task_id = f"task_{len(st.session_state.tasks_data) + 1}"
                task_data["status"] = "Pending"
                task_data["progress"] = 0
                st.session_state.tasks_data[task_id] = task_data
                st.success(f"Task {task_id} added successfully!")
                st.rerun()
    
    with col2:
        st.subheader("Current Tasks")
        
        if st.session_state.tasks_data:
            for task_id, task_data in st.session_state.tasks_data.items():
                with st.expander(f"{task_id}: {task_data['task_type']}", expanded=True):
                    col3, col4, col5 = st.columns([2, 1, 1])
                    
                    with col3:
                        st.json(task_data)
                    
                    with col4:
                        if st.button(f"▶️ Start", key=f"start_{task_id}"):
                            st.session_state.tasks_data[task_id]["status"] = "Running"
                            st.rerun()
                    
                    with col5:
                        if st.button(f"🗑️ Delete", key=f"delete_{task_id}"):
                            del st.session_state.tasks_data[task_id]
                            st.rerun()
        else:
            st.info("No tasks added yet. Create your first task!")

# Page 4: Real-time Analysis
elif page == "📊 Real-time Analysis":
    st.markdown('<div class="main-header"><h2>📊 Real-time Analysis Dashboard</h2></div>', unsafe_allow_html=True)
    
    if not st.session_state.cells_data:
        st.warning("No cells configured. Please go to 'Setup Cells' first.")
    else:
        # Control panel
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("▶️ Start Simulation", use_container_width=True):
                st.session_state.simulation_running = True
        
        with col2:
            if st.button("⏸️ Pause Simulation", use_container_width=True):
                st.session_state.simulation_running = False
        
        with col3:
            if st.button("🔄 Update Data", use_container_width=True):
                simulate_real_time_data()
                st.rerun()
        
        with col4:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.historical_data = []
                st.session_state.current_time = 0
        
        # Auto-refresh when simulation is running
        if st.session_state.simulation_running:
            simulate_real_time_data()
            time.sleep(1)
            st.rerun()
        
        # Real-time metrics
        st.subheader("📈 Live Metrics")
        
        metrics_cols = st.columns(len(st.session_state.cells_data))
        for idx, (cell_id, cell_data) in enumerate(st.session_state.cells_data.items()):
            with metrics_cols[idx]:
                st.metric(
                    f"{cell_id}",
                    f"{cell_data['voltage']:.2f}V",
                    f"{cell_data['temp']:.1f}°C"
                )
        
        # Charts
        if st.session_state.historical_data:
            df_hist = pd.DataFrame(st.session_state.historical_data)
            
            # Voltage chart
            fig_voltage = px.line(
                df_hist, 
                x='timestamp', 
                y='voltage', 
                color='cell_id',
                title="📊 Cell Voltage Over Time",
                labels={'voltage': 'Voltage (V)', 'timestamp': 'Time'}
            )
            fig_voltage.update_layout(height=400)
            st.plotly_chart(fig_voltage, use_container_width=True)
            
            # Temperature and Current charts
            col5, col6 = st.columns(2)
            
            with col5:
                fig_temp = px.line(
                    df_hist,
                    x='timestamp',
                    y='temp',
                    color='cell_id',
                    title="🌡️ Temperature Monitoring"
                )
                st.plotly_chart(fig_temp, use_container_width=True)
            
            with col6:
                fig_current = px.line(
                    df_hist,
                    x='timestamp',
                    y='current',
                    color='cell_id',
                    title="⚡ Current Flow"
                )
                st.plotly_chart(fig_current, use_container_width=True)
        
        # Task progress
        if st.session_state.tasks_data:
            st.subheader("📋 Task Progress")
            
            for task_id, task_data in st.session_state.tasks_data.items():
                if task_data["status"] == "Running":
                    # Simulate progress
                    progress = min(100, task_data.get("progress", 0) + random.randint(1, 5))
                    st.session_state.tasks_data[task_id]["progress"] = progress
                    
                    if progress >= 100:
                        st.session_state.tasks_data[task_id]["status"] = "Completed"
                
                col7, col8 = st.columns([3, 1])
                with col7:
                    st.progress(task_data.get("progress", 0) / 100, f"{task_id}: {task_data['task_type']}")
                with col8:
                    st.write(f"{task_data['status']} ({task_data.get('progress', 0)}%)")

# Page 5: Data Export
elif page == "📥 Data Export":
    st.markdown('<div class="main-header"><h2>📥 Data Export & Summary</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Cell Data Summary")
        
        if st.session_state.cells_data:
            df_cells = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
            st.dataframe(df_cells, use_container_width=True)
            
            # Export cell data
            csv_cells = df_cells.to_csv(index=True)
            st.download_button(
                label="📥 Download Cell Data (CSV)",
                data=csv_cells,
                file_name=f"battery_cells_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No cell data available for export.")
    
    with col2:
        st.subheader("📋 Task Data Summary")
        
        if st.session_state.tasks_data:
            df_tasks = pd.DataFrame.from_dict(st.session_state.tasks_data, orient='index')
            st.dataframe(df_tasks, use_container_width=True)
            
            # Export task data
            csv_tasks = df_tasks.to_csv(index=True)
            st.download_button(
                label="📥 Download Task Data (CSV)",
                data=csv_tasks,
                file_name=f"battery_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No task data available for export.")
    
    # Historical data export
    if st.session_state.historical_data:
        st.subheader("📈 Historical Data")
        
        df_historical = pd.DataFrame(st.session_state.historical_data)
        st.dataframe(df_historical.tail(100), use_container_width=True)  # Show last 100 records
        
        csv_historical = df_historical.to_csv(index=False)
        st.download_button(
            label="📥 Download Historical Data (CSV)",
            data=csv_historical,
            file_name=f"battery_historical_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Statistics
        st.subheader("📊 Data Statistics")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.metric("Total Records", len(df_historical))
        
        with col4:
            if len(df_historical) > 0:
                st.metric("Avg Voltage", f"{df_historical['voltage'].mean():.2f}V")
        
        with col5:
            if len(df_historical) > 0:
                st.metric("Avg Temperature", f"{df_historical['temp'].mean():.1f}°C")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔋 Battery Simulator v1.0")
st.sidebar.markdown("Built with Streamlit & Plotly")
