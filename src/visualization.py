import matplotlib.pyplot as plt
import numpy as np

class TrafficVisualizer:
    def __init__(self, grid_size=4):
        """Initialize traffic visualization with grid size"""
        self.grid_size = grid_size
        self.fig = None
        self.ax = None
    
    def setup_plot(self):
        """Set up the plot for visualization"""
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        
        # Set up grid
        self.ax.set_xlim(-0.5, self.grid_size - 0.5)
        self.ax.set_ylim(-0.5, self.grid_size - 0.5)
        self.ax.set_xticks(range(self.grid_size))
        self.ax.set_yticks(range(self.grid_size))
        self.ax.grid(True)
        
        # Labels
        self.ax.set_title("Traffic Management System")
        self.ax.set_xlabel("East-West")
        self.ax.set_ylabel("North-South")
        
        return self.fig, self.ax
    
    def visualize_traffic(self, intersections, emergencies=None, step=0, save_path=None):
        """Create a visualization of the current traffic state"""
        if self.fig is None or self.ax is None:
            self.setup_plot()
        else:
            self.ax.clear()
            self.ax.set_xlim(-0.5, self.grid_size - 0.5)
            self.ax.set_ylim(-0.5, self.grid_size - 0.5)
            self.ax.grid(True)
        
        # Plot intersections
        for intersection in intersections:
            x, y = intersection.location
            
            # Determine color based on signal phase and emergency mode
            if intersection.emergency_mode:
                color = 'purple'
            else:
                color = 'green' if intersection.current_phase == 0 else 'red'
            
            # Size based on number of waiting vehicles
            waiting = sum(intersection.waiting_vehicles.values())
            size = 100 + (waiting / 2)
            
            self.ax.scatter(x, y, color=color, s=size, alpha=0.7)
            self.ax.text(x, y+0.1, f"{intersection.intersection_id}", fontsize=8, ha='center')
            
            # Show waiting vehicles count with varied position to avoid overlap
            self.ax.text(x, y-0.15, f"{waiting}", fontsize=7, ha='center')
            
            # Display more detailed traffic info on selected intersections
            if x == 0 and y == 0 or x == self.grid_size-1 and y == self.grid_size-1:
                details = f"N:{intersection.waiting_vehicles['north']} S:{intersection.waiting_vehicles['south']}"
                details2 = f"E:{intersection.waiting_vehicles['east']} W:{intersection.waiting_vehicles['west']}"
                self.ax.text(x, y-0.25, details, fontsize=6, ha='center')
                self.ax.text(x, y-0.35, details2, fontsize=6, ha='center')
        
        # Plot emergency vehicles
        if emergencies:
            for vehicle_id, emergency in emergencies.items():
                if emergency["status"] == "active" or emergency["status"] == "completed":
                    path = emergency["path"]
                    pos_idx = emergency["current_position"]
                    
                    if pos_idx < len(path):
                        x, y = path[pos_idx]
                        self.ax.scatter(x, y, color='blue', marker='*', s=200, zorder=10)
                        self.ax.text(x, y+0.2, f"EV: {vehicle_id}", fontsize=9, ha='center')
                        
                        # Draw path
                        path_x = [p[0] for p in path[:pos_idx+1]]
                        path_y = [p[1] for p in path[:pos_idx+1]]
                        future_x = [p[0] for p in path[pos_idx:]]
                        future_y = [p[1] for p in path[pos_idx:]]
                        
                        self.ax.plot(path_x, path_y, 'b-', alpha=0.7, linewidth=2)
                        self.ax.plot(future_x, future_y, 'b--', alpha=0.4, linewidth=2)
                        
                        # Add direction arrow
                        if pos_idx > 0:
                            prev_x, prev_y = path[pos_idx-1]
                            dx, dy = x - prev_x, y - prev_y
                            if dx != 0 or dy != 0:  # Avoid zero-length arrow
                                self.ax.arrow(x-dx*0.3, y-dy*0.3, dx*0.2, dy*0.2, 
                                            head_width=0.1, head_length=0.1, 
                                            fc='blue', ec='blue', zorder=11)
        
        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='N-S Green'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='E-W Green'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', markersize=10, label='Emergency Mode'),
            Line2D([0], [0], marker='*', color='w', markerfacecolor='blue', markersize=10, label='Emergency Vehicle')
        ]
        self.ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4)
        
        # Update title with step
        self.ax.set_title(f"Traffic Management System - Step {step}")
        
        # Save if needed
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
            return save_path
        
        return self.fig
    
    def plot_metrics(self, metrics, save_path=None):
        """Plot performance metrics"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot average wait times
        if "average_wait_time" in metrics and metrics["average_wait_time"]:
            ax1.plot(metrics["average_wait_time"], 'b-', linewidth=2, marker='o')
            ax1.set_title("Average Waiting Vehicles")
            ax1.set_xlabel("Simulation Step")
            ax1.set_ylabel("Number of Vehicles")
            ax1.grid(True)
            
            # Add trendline
            import numpy as np
            if len(metrics["average_wait_time"]) > 1:
                x = np.arange(len(metrics["average_wait_time"]))
                z = np.polyfit(x, metrics["average_wait_time"], 1)
                p = np.poly1d(z)
                ax1.plot(x, p(x), "r--", alpha=0.7, label=f"Trend: {z[0]:.2f}x + {z[1]:.2f}")
                ax1.legend()
        
        # Plot fairness index
        if "fairness_index" in metrics and metrics["fairness_index"]:
            ax2.plot(metrics["fairness_index"], 'g-', linewidth=2, marker='o')
            ax2.set_title("Traffic Distribution Fairness")
            ax2.set_xlabel("Simulation Step")
            ax2.set_ylabel("Fairness Index (0-1)")
            ax2.set_ylim(0, 1.05)
            ax2.grid(True)
            
            # Add average line
            if metrics["fairness_index"]:
                avg_fairness = sum(metrics["fairness_index"]) / len(metrics["fairness_index"])
                ax2.axhline(y=avg_fairness, color='r', linestyle='--', 
                            label=f"Avg: {avg_fairness:.3f}")
                ax2.legend()
        
        plt.tight_layout()
        
        # Save if needed
        if save_path:
            plt.savefig(save_path)
            return save_path
        
        return fig
    
    def plot_emergency_comparison(self, normal_time, emergency_time, save_path=None):
        """Plot comparison of emergency response times"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create bar chart
        labels = ['Without Priority', 'With Priority']
        times = [normal_time, emergency_time]
        bars = ax.bar(labels, times, color=['gray', 'blue'])
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{int(height)}s',
                    ha='center', va='bottom')
        
        # Calculate improvement percentage
        if normal_time > 0:
            improvement = (normal_time - emergency_time) / normal_time * 100
            plt.title(f"Emergency Response Time Comparison\n{improvement:.1f}% Improvement")
        else:
            plt.title("Emergency Response Time Comparison")
        
        ax.set_ylabel("Response Time (seconds)")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Save if needed
        if save_path:
            plt.savefig(save_path)
            return save_path
        
        return fig