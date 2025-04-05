import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import os

# Page configuration
st.set_page_config(page_title="TrafficSync Dashboard", layout="wide")

# Header
st.title("TrafficSync: Multi-Agent System for Smart Traffic Management")
st.markdown("---")

# Key metrics in columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Normal Response Time", value="360s")
with col2:
    st.metric(label="Emergency Response Time", value="120s")
with col3:
    st.metric(label="Improvement", value="66.7%", delta="Faster")
with col4:
    st.metric(label="Fairness Index", value="0.997", help="1.0 is perfectly fair")

# Main results section
st.header("Emergency Response Time Comparison")
emergency_img = Image.open("output/emergency_comparison.png")
st.image(emergency_img, use_column_width=True)

st.header("Performance Metrics")
metrics_img = Image.open("output/performance_metrics.png")
st.image(metrics_img, use_column_width=True)

# Interactive simulation steps
st.header("Simulation Visualization")
step_files = [f for f in os.listdir("output") if f.startswith("step_") and f.endswith(".png")]
step_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]) if x.split("_")[1].split(".")[0].isdigit() else 0)

step_options = [f.replace("step_", "Step ").replace(".png", "") for f in step_files]
selected_step = st.select_slider("Select simulation step:", options=step_options)

selected_file = f"output/step_{selected_step.replace('Step ', '')}.png"
step_img = Image.open(selected_file)
st.image(step_img, use_column_width=True)

# Explanation section
st.header("Understanding the Visualization")
with st.expander("Click to see explanation"):
    st.markdown("""
    ### Color Legend:
    - **Green circles**: Traffic signals giving priority to North-South traffic
    - **Red circles**: Traffic signals giving priority to East-West traffic
    - **Purple circles**: Signals in emergency mode
    - **Blue star**: Emergency vehicle
    
    ### Key Features:
    - Numbers below each intersection show waiting vehicles
    - Blue lines show the emergency vehicle's planned path
    - Details like "N:10 S:11" show waiting vehicles in each direction
    """)

# System description
st.header("About TrafficSync")
st.markdown("""
TrafficSync is a multi-agent system for smart traffic management that:

1. Dynamically adjusts traffic signals based on real-time conditions
2. Creates priority corridors for emergency vehicles, reducing response times by 66.7%
3. Maintains fairness in traffic distribution across the network
4. Simulates various urban traffic scenarios including rush hour and emergency events

The system uses a grid of AI-powered traffic signal agents that communicate and coordinate to optimize overall traffic flow.
""")