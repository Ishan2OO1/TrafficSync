# TrafficSync: Multi-Agent System for Smart Traffic Management

A multi-agent AI system for optimizing urban traffic flow and emergency vehicle response times.

## Overview

TrafficSync uses AI agents to analyze real-time traffic data, dynamically adjust signal timing, and create priority corridors for emergency vehicles. The system ensures fairness in traffic distribution while minimizing overall congestion.

## Key Results

- **Normal response time:** 360 seconds
- **Emergency response time:** 120 seconds
- **Improvement:** 66.7% faster emergency response
- **Fairness index:** 0.997 (very fair)
- **Average wait time:** 40.5 vehicles per intersection

## Features

- **Dynamic Signal Control:** AI agents analyze real-time traffic data and adjust signal timing
- **Emergency Vehicle Priority:** Creates green corridors for emergency vehicles
- **Fairness Optimization:** Prevents excessive delays in specific areas
- **Multi-Agent Architecture:** Traffic signals communicate and coordinate for system-wide optimization
- **Data-Driven:** Uses real traffic patterns to simulate various urban scenarios

## Architecture

The system consists of multiple AI agents working together:

- **Signal Control Agents:** Manage individual intersections based on local traffic conditions
- **Zone Coordinator Agents:** Optimize traffic patterns across multiple intersections
- **Emergency Response Agent:** Creates priority routing for emergency vehicles
- **Data Processing Agent:** Analyzes traffic patterns and provides insights

## Project Structure

- `src/` - Source code for the simulation
  - `agents.py` - Implementation of AI agents for traffic management
  - `data_processor.py` - Traffic data processing utilities
  - `simulation.py` - Core simulation environment
  - `visualization.py` - Traffic visualization tools
- `output/` - Simulation result images
- `data/` - Traffic datasets
- `main.py` - Entry point for running the simulation
- `dashboard.py` - Interactive Streamlit dashboard

## Setup

1. Clone this repository
2. Install dependencies: pip install -r requirements.txt
3. Run the simulation: python main.py

## Dashboard

For an interactive visualization of results, run the Streamlit dashboard: streamlit run dashboard.py


This project was created for the AI Multi-Agent Systems Hackathon.
