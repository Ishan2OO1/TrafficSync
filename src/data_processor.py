import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataProcessor:
    def __init__(self, csv_path):
        """Initialize with path to traffic data CSV file"""
        self.df = self.load_traffic_data(csv_path)
        
   
    def load_traffic_data(self, csv_path):
        """Load and prepare the traffic dataset"""
        df = pd.read_csv(csv_path)
    
        # Check column names and adapt to the actual format
        print("Available columns:", df.columns.tolist())  # For debugging
    
        # Handle different column naming conventions
        if 'Traffic Situation' in df.columns:
            df.rename(columns={'Traffic Situation': 'TrafficSituation'}, inplace=True)
    
        # Convert traffic situation to descriptive categories if numerical
        if pd.api.types.is_numeric_dtype(df['TrafficSituation']):
        # If values are already numeric
            traffic_map = {1: "Heavy", 2: "High", 3: "Normal", 4: "Low"}
            df['TrafficSituation'] = df['TrafficSituation'].map(traffic_map)
        elif df['TrafficSituation'].str.lower().isin(['low', 'normal', 'high', 'heavy']).all():
            # If values are text but lowercase
            df['TrafficSituation'] = df['TrafficSituation'].str.capitalize()
    
        # Generate datetime column for easier filtering
        if 'Time' in df.columns and 'Date' in df.columns:
            # Your data has Time and Date columns
            df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), 
                                        format='%d %I:%M:%S %p', errors='coerce')
    
        return df
        
    def get_traffic_for_time(self, target_time):
        """Get traffic data for a specific time"""
        # Convert string to datetime if needed
        if isinstance(target_time, str):
            target_time = pd.to_datetime(target_time)
    
        # If DateTime conversion worked
        if 'DateTime' in self.df.columns:
            # Find closest time in dataset
            time_diff = abs(self.df['DateTime'] - target_time)
            closest_index = time_diff.idxmin()
        else:
            # Fallback to using the first row
            closest_index = 0
    
        return self.df.iloc[closest_index]
    
    
    
    def get_traffic_scenario(self, scenario_type):
        """Get traffic data for predefined scenarios"""
        if scenario_type == "rush_hour_morning":
            # Filter for weekday morning rush hour (8-9 AM)
            return self.df[(self.df['DateTime'].dt.hour == 8) & 
                          (self.df['DateTime'].dt.dayofweek < 5)]
        
        elif scenario_type == "rush_hour_evening":
            # Filter for weekday evening rush hour (5-6 PM)
            return self.df[(self.df['DateTime'].dt.hour == 17) & 
                          (self.df['DateTime'].dt.dayofweek < 5)]
        
        elif scenario_type == "weekend":
            # Filter for weekend daytime
            return self.df[(self.df['DateTime'].dt.dayofweek >= 5) & 
                          (self.df['DateTime'].dt.hour >= 10) & 
                          (self.df['DateTime'].dt.hour <= 18)]
        
        elif scenario_type == "low_traffic":
            # Filter for late night (11 PM - 5 AM)
            return self.df[(self.df['DateTime'].dt.hour >= 23) | 
                          (self.df['DateTime'].dt.hour <= 5)]
        
        else:
            # Default to returning the full dataset
            return self.df
    
    def distribute_traffic_by_direction(self, traffic_data):
        """Distribute traffic across directions based on time of day and add randomness"""
        total_vehicles = traffic_data['Total']
        
        # Try to get the hour, with fallback if parsing fails
        try:
            if 'Time' in traffic_data:
                time_str = traffic_data['Time']
                if isinstance(time_str, str) and ':' in time_str:
                    hour = int(time_str.split(':')[0])
                    # Handle AM/PM format
                    if 'PM' in time_str.upper() and hour < 12:
                        hour += 12
                    elif 'AM' in time_str.upper() and hour == 12:
                        hour = 0
            else:
                # Default to mid-day if we can't parse
                hour = 12
        except:
            hour = 12  # Default fallback
        
        # Create different distribution patterns based on time of day
        if 7 <= hour <= 9:  # Morning rush - heavy inbound
            base_distribution = {"north": 0.4, "south": 0.2, "east": 0.3, "west": 0.1}
        elif 16 <= hour <= 18:  # Evening rush - heavy outbound
            base_distribution = {"north": 0.2, "south": 0.4, "east": 0.1, "west": 0.3}
        else:  # Normal distribution
            base_distribution = {"north": 0.25, "south": 0.25, "east": 0.25, "west": 0.25}
        
        # Add randomness to make distribution more realistic
        import random
        distribution = {}
        for direction, base_ratio in base_distribution.items():
            # Add ±20% random variation
            variation = random.uniform(-0.2, 0.2) * base_ratio
            distribution[direction] = max(0.05, base_ratio + variation)  # Ensure minimum 5%
        
        # Normalize to ensure ratios sum to 1.0
        total = sum(distribution.values())
        distribution = {k: v/total for k, v in distribution.items()}
        
        # Create vehicle counts by direction and type
        result = {}
        for direction, ratio in distribution.items():
            # Add some randomness to total count too
            direction_total = int(total_vehicles * ratio * random.uniform(0.8, 1.2))
            
            result[direction] = {
                "cars": int(traffic_data['CarCount'] * ratio),
                "bikes": int(traffic_data['BikeCount'] * ratio),
                "buses": int(traffic_data['BusCount'] * ratio),
                "trucks": int(traffic_data['TruckCount'] * ratio),
                "total": direction_total
            }
        
        return result
