import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SignalControlAgent:
    def __init__(self, intersection_id, location=(0, 0)):
        """Initialize a traffic signal control agent"""
        self.intersection_id = intersection_id
        self.location = location  # (x, y) coordinates for visualization
        self.current_phase = 0  # 0=N-S Green, 1=E-W Green
        self.phase_duration = 30  # Default duration in seconds
        self.time_in_phase = 0  # Time elapsed in current phase
        self.emergency_mode = False
        self.waiting_vehicles = {"north": 0, "south": 0, "east": 0, "west": 0}
        self.historical_wait_times = []
        
    def process_traffic_data(self, distributed_traffic):
        """Process traffic data and adjust signal timing"""
        # Update waiting vehicles based on distributed traffic
        for direction, vehicles in distributed_traffic.items():
            self.waiting_vehicles[direction] = vehicles["total"]
        
        # Calculate optimal timing if not in emergency mode
        if not self.emergency_mode:
            self._calculate_optimal_timing()
        
        # Track historical wait times for fairness metrics
        total_waiting = sum(self.waiting_vehicles.values())
        self.historical_wait_times.append(total_waiting)
        if len(self.historical_wait_times) > 12:  # Keep last hour (12 x 5min)
            self.historical_wait_times.pop(0)
        
        return {
            "intersection_id": self.intersection_id,
            "current_phase": self.current_phase,
            "phase_duration": self.phase_duration,
            "waiting_vehicles": self.waiting_vehicles,
            "emergency_mode": self.emergency_mode
        }
    
    def update(self, time_step):
        """Update signal state based on time passing"""
        # Increment time in current phase
        self.time_in_phase += time_step
        
        # Check if it's time to switch phases
        if self.time_in_phase >= self.phase_duration:
            self.switch_phase()
            return True  # Phase was switched
        
        return False  # No phase change
    
    def switch_phase(self):
        """Switch the signal phase"""
        self.current_phase = 1 - self.current_phase  # Toggle between 0 and 1
        self.time_in_phase = 0  # Reset time in phase
        
        # Process vehicles that get to go during the phase switch
        if self.current_phase == 0:  # N-S gets green
            self._process_movement("north", "south")
        else:  # E-W gets green
            self._process_movement("east", "west")
    
    def _process_movement(self, dir1, dir2):
        """Process vehicles moving through the intersection"""
        # Simple model: 70% of waiting vehicles get through during a green phase
        cleared1 = int(self.waiting_vehicles[dir1] * 0.7)
        cleared2 = int(self.waiting_vehicles[dir2] * 0.7)
        
        self.waiting_vehicles[dir1] -= cleared1
        self.waiting_vehicles[dir2] -= cleared2
    
    def _calculate_optimal_timing(self):
        """Calculate optimal signal timing based on waiting vehicles"""
        # Simple calculation based on waiting vehicles
        ns_total = self.waiting_vehicles["north"] + self.waiting_vehicles["south"]
        ew_total = self.waiting_vehicles["east"] + self.waiting_vehicles["west"]
        
        # Base timing is 30 seconds
        base_timing = 30
        
        # Adjust phase duration based on waiting vehicles ratio
        if self.current_phase == 0:  # Currently N-S has green
            if ns_total > ew_total:
                ratio = min(3, ns_total / max(1, ew_total))  # Cap at 3x
                self.phase_duration = int(base_timing * ratio)
            else:
                # If E-W has more, shorten current phase
                self.phase_duration = max(15, base_timing // 2)
        else:  # Currently E-W has green
            if ew_total > ns_total:
                ratio = min(3, ew_total / max(1, ns_total))  # Cap at 3x
                self.phase_duration = int(base_timing * ratio)
            else:
                # If N-S has more, shorten current phase
                self.phase_duration = max(15, base_timing // 2)
        
        # Cap duration for fairness
        self.phase_duration = min(90, self.phase_duration)  # Maximum 90 seconds per phase
    
    def switch_to_emergency_mode(self, direction):
        """Switch to emergency mode to prioritize given direction"""
        self.emergency_mode = True
        
        # Set phase to allow emergency vehicle through
        if direction in ["north", "south"]:
            target_phase = 0
        else:
            target_phase = 1
        
        # If not already in the correct phase, switch immediately
        if self.current_phase != target_phase:
            self.current_phase = target_phase
            self.time_in_phase = 0
        
        # Set long duration to keep phase
        self.phase_duration = 60
        
        return {
            "status": "emergency_mode_activated",
            "intersection_id": self.intersection_id,
            "phase": self.current_phase
        }
    
    def exit_emergency_mode(self):
        """Return to normal operation after emergency"""
        self.emergency_mode = False
        self._calculate_optimal_timing()
        return {"status": "normal_operation_resumed"}
    
    def get_fairness_metrics(self):
        """Calculate fairness metrics for this intersection"""
        if not self.historical_wait_times:
            return {"fairness_index": 1.0}
        
        # Calculate Jain's fairness index over time
        n = len(self.historical_wait_times)
        squared_sum = sum(w**2 for w in self.historical_wait_times)
        sum_squared = sum(self.historical_wait_times)**2
        
        if squared_sum == 0:
            return {"fairness_index": 1.0}
            
        fairness = sum_squared / (n * squared_sum)
        
        return {
            "fairness_index": fairness,
            "max_wait": max(self.historical_wait_times),
            "avg_wait": sum(self.historical_wait_times) / n
        }


class EmergencyVehicleAgent:
    def __init__(self):
        """Initialize the emergency vehicle coordinator agent"""
        self.active_emergencies = {}
        self.completed_emergencies = {}
        self.grid_size = 4  # Default 4x4 grid
    
    def set_grid_size(self, size):
        """Set the grid size for path planning"""
        self.grid_size = size
    
    def dispatch_vehicle(self, vehicle_id, start_point, end_point, priority=1):
        """Dispatch an emergency vehicle with a planned route"""
        # Create a path (for demo using simple grid coordinates)
        path = self._generate_path(start_point, end_point)
        
        # Record emergency vehicle
        self.active_emergencies[vehicle_id] = {
            "path": path,
            "current_position": 0,  # Index in path
            "start_point": start_point,
            "end_point": end_point,
            "priority": priority,
            "start_time": pd.Timestamp.now(),
            "status": "active",
            "intersections_cleared": []
        }
        
        # Return first 3 intersections that need to be notified
        notify_length = min(3, len(path))
        
        return {
            "vehicle_id": vehicle_id,
            "notify_intersections": path[:notify_length],
            "priority": priority,
            "status": "dispatched"
        }
    
    def _generate_path(self, start, end):
        """Generate a path from start to end point
        
        In this simplified version, we assume:
        - start and end are (x,y) tuples with grid coordinates
        - We'll use a simple A* path on the grid
        """
        # For demo purposes, generate a simple path
        path = []
        
        # Extract coordinates
        start_x, start_y = start
        end_x, end_y = end
        
        # Generate path along x direction first, then y
        current_x, current_y = start_x, start_y
        
        # Move along x-axis
        while current_x != end_x:
            if current_x < end_x:
                current_x += 1
            else:
                current_x -= 1
            path.append((current_x, current_y))
        
        # Then move along y-axis
        while current_y != end_y:
            if current_y < end_y:
                current_y += 1
            else:
                current_y -= 1
            path.append((current_x, current_y))
        
        return path
    
    def update_position(self, vehicle_id, steps=1):
        """Update the position of an emergency vehicle"""
        if vehicle_id not in self.active_emergencies:
            return {"error": "Vehicle not found"}
            
        emergency = self.active_emergencies[vehicle_id]
        
        # Get current position index
        current_idx = emergency["current_position"]
        
        # Calculate new position
        new_idx = min(current_idx + steps, len(emergency["path"]) - 1)
        emergency["current_position"] = new_idx
        
        # Get new coordinates
        new_position = emergency["path"][new_idx]
        
        # Check if we need to notify new intersections
        notify_intersections = []
        for i in range(1, 4):  # Look 3 steps ahead
            if new_idx + i < len(emergency["path"]):
                next_pos = emergency["path"][new_idx + i]
                if next_pos not in emergency["intersections_cleared"]:
                    notify_intersections.append(next_pos)
                    emergency["intersections_cleared"].append(next_pos)
        
        # Check if reached destination
        if new_idx >= len(emergency["path"]) - 1:
            emergency["status"] = "completed"
            # Don't remove the emergency from active_emergencies immediately
            # to allow it to be visualized at the final position
            # Just mark it as completed
            
            # Calculate travel time - don't move to completed yet
            travel_time = (pd.Timestamp.now() - emergency["start_time"]).total_seconds()
            emergency["travel_time"] = travel_time
            
            return {
                "status": "completed",
                "vehicle_id": vehicle_id,
                "travel_time": travel_time
            }
            
        # Return updated status
        return {
            "vehicle_id": vehicle_id,
            "current_position": new_position,
            "notify_intersections": notify_intersections,
            "status": "active"
        }
    
    def get_metrics(self):
        """Get metrics on emergency vehicle performance"""
        if not self.completed_emergencies:
            return {
                "total_emergencies": len(self.active_emergencies),
                "completed_emergencies": 0,
                "avg_travel_time": None
            }
        
        # Calculate metrics
        travel_times = [e["travel_time"] for e in self.completed_emergencies.values()]
        
        return {
            "total_emergencies": len(self.active_emergencies) + len(self.completed_emergencies),
            "completed_emergencies": len(self.completed_emergencies),
            "avg_travel_time": sum(travel_times) / len(travel_times),
            "min_travel_time": min(travel_times),
            "max_travel_time": max(travel_times)
        }