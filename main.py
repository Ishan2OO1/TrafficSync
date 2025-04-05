import os
import pandas as pd
from src.data_processor import DataProcessor
from src.agents import SignalControlAgent, EmergencyVehicleAgent
from src.simulation import TrafficSimulation
from src.visualization import TrafficVisualizer

def main():
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    # Set the data path
    data_path = "data/Traffic.csv"
    
    # Check if dataset exists, otherwise create dummy data
    if not os.path.exists(data_path):
        print("Dataset not found. Creating dummy dataset for demonstration...")
        create_dummy_dataset(data_path)
    else:
        print(f"Using existing dataset at {data_path}")
    
    # Initialize data processor
    data_processor = DataProcessor(data_path)
    
    print("Running emergency vehicle scenario...")
    simulation = TrafficSimulation(data_processor, grid_size=4)  # Create fresh simulation
    metrics = simulation.run_simulation(steps=24, visualize=True, emergency_scenario=True)
    
    # Print final metrics with proper error handling
    print("\nSimulation Results:")
    if metrics is not None:  # First check if metrics exists
        normal_time = metrics.get("normal_response_time")
        emergency_time = metrics.get("emergency_response_time")
        
        if normal_time is not None and emergency_time is not None and normal_time > 0:
            improvement = (normal_time - emergency_time) / normal_time * 100
            print(f"Normal response time: {normal_time:.1f} seconds")
            print(f"Emergency response time: {emergency_time:.1f} seconds")
            print(f"Improvement: {improvement:.1f}%")
        else:
            print("Response time metrics not available or invalid")
        
        # Safely access other metrics
        if "average_wait_time" in metrics and metrics["average_wait_time"]:
            print(f"Average wait time: {metrics['average_wait_time'][-1]:.1f} vehicles")
        
        if "fairness_index" in metrics and metrics["fairness_index"]:
            print(f"Fairness index: {metrics['fairness_index'][-1]:.3f} (1.0 is perfectly fair)")
    else:
        print("No metrics data available")
    
    print("\nVisualization outputs saved to 'output/' directory")

def create_dummy_dataset(path):
    """Create a dummy dataset for demonstration purposes"""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Generate dates and times
    dates = []
    times = []
    traffic_situations = []
    car_counts = []
    bike_counts = []
    bus_counts = []
    truck_counts = []
    totals = []
    
    # Generate 7 days of data at 15-minute intervals
    start_date = pd.Timestamp('2023-01-01')
    for day in range(7):
        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                current_time = start_date + pd.Timedelta(days=day, hours=hour, minutes=minute)
                
                # Format date and time
                dates.append(current_time.strftime('%Y-%m-%d'))
                times.append(current_time.strftime('%H:%M'))
                
                # Generate traffic based on time of day
                if 7 <= hour <= 9:  # Morning rush hour
                    situation = 1 if minute >= 30 else 2  # Heavy/High
                    cars = 80 + int(30 * ((hour - 7) * 60 + minute) / 180)  # Ramp up
                    bikes = 15 + int(10 * ((hour - 7) * 60 + minute) / 180)
                    buses = 5 + int(5 * ((hour - 7) * 60 + minute) / 180)
                    trucks = 10 + int(5 * ((hour - 7) * 60 + minute) / 180)
                elif 16 <= hour <= 18:  # Evening rush hour
                    situation = 1 if minute >= 30 else 2  # Heavy/High
                    cars = 90 + int(30 * ((hour - 16) * 60 + minute) / 180)  # Ramp up
                    bikes = 10 + int(5 * ((hour - 16) * 60 + minute) / 180)
                    buses = 5 + int(5 * ((hour - 16) * 60 + minute) / 180)
                    trucks = 5 + int(3 * ((hour - 16) * 60 + minute) / 180)
                elif 22 <= hour or hour <= 5:  # Late night/early morning
                    situation = 4  # Low
                    cars = 10 + hour % 5
                    bikes = 2 + hour % 3
                    buses = 1
                    trucks = 2 + hour % 2
                else:  # Normal daytime
                    situation = 3  # Normal
                    cars = 40 + (hour % 7) * 5
                    bikes = 5 + (hour % 5) * 2
                    buses = 3 + hour % 3
                    trucks = 5 + hour % 5
                
                # Weekend adjustment
                if day >= 5:  # Saturday and Sunday
                    cars = int(cars * 0.7)
                    bikes = int(bikes * 0.5)
                    buses = int(buses * 0.5)
                    trucks = int(trucks * 0.3)
                    situation = min(situation + 1, 4)  # Reduce congestion
                
                total = cars + bikes + buses + trucks
                
                # Append to lists
                traffic_situations.append(situation)
                car_counts.append(cars)
                bike_counts.append(bikes)
                bus_counts.append(buses)
                truck_counts.append(trucks)
                totals.append(total)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'TimeInHour': times,
        'Day': [(start_date + pd.Timedelta(days=d)).day_name() for d in range(7)] * (24 * 4),
        'TrafficSituation': traffic_situations,
        'CarCount': car_counts,
        'BikeCount': bike_counts,
        'BusCount': bus_counts,
        'TruckCount': truck_counts,
        'Total': totals
    })
    
    # Save to CSV
    df.to_csv(path, index=False)
    print(f"Dummy dataset created at {path}")

if __name__ == "__main__":
    main()