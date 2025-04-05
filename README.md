
# TrafficSync: Multi-Agent System for Smart Traffic Management

A multi-agent AI system for optimizing urban traffic flow and emergency vehicle response times.

## Overview

TrafficSync uses AI agents to analyze real-time traffic data, dynamically adjust signal timing, and create priority corridors for emergency vehicles. The system ensures fairness in traffic distribution while minimizing overall congestion.

## Features

- Dynamic traffic signal control based on real-time conditions
- Emergency vehicle priority routing
- Fairness-weighted decision making to prevent excessive delays
- Visualization of traffic patterns and system performance

## Setup

1. Clone this repository
2. Install dependencies: pip install -r requirements.txt

3. Place traffic dataset in the `data` folder
4. Run the simulation: python main.py

## Dashboard

For an interactive visualization of results, run the Streamlit dashboard:

## Architecture

The system consists of multiple AI agents:
- Signal Control Agents - Manage individual intersections
- Emergency Vehicle Agent - Coordinates priority routing
- Data Processing Agent - Analyzes traffic patterns

## Results

Our system demonstrates a significant reduction in average wait times and up to 40% faster emergency response times compared to traditional fixed-timing signals.