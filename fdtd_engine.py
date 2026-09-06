import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ==========================================
# Material Properties
# ==========================================
class Material:
    def __init__(self, name, epsilon_r, metalic_loss):
        self.name = name
        self.epsilon_r = epsilon_r
        self.metalic_loss = metalic_loss # 0.0 for dielectrics, >0 for conductors

# ==========================================
# Core Engine: FDTD Simulator
# ==========================================
class FDTDSimulator:
    def __init__(self, size, source_type="gaussian"): 
        # Setting physical space and variables
        self.size = size
        self.imp0 = 377.0 # Impedance of free space (in Ohms)
        self.time_step = 0 
        self.source_type = source_type # "gaussian" or "sine"
        
        # Setting the vectors which represent the field at any point in space
        self.electric_field_z = np.zeros(size)
        self.magnetic_field_y = np.zeros(size)
        
        # Setting material grids (Default is vacuum/air)
        self.dielectric_value = np.ones(size)
        self.metalic_loss = np.zeros(size)
        
        # Setting coefficient grids for loss calculations
        self.loss_calc1 = np.ones(size)
        self.loss_calc2 = np.ones(size)
        
        # Setting physical memory for visualization and data collection
        self.materials_map = []
        self.sensor_input = []
        self.sensor_output = []
        
        # Default sensor locations (will update dynamically based on material)
        self.sensor_in_idx = 55
        self.sensor_out_idx = 320
    
    def add_material(self, start_idx, end_idx, material):
        # Apply material properties to specific grid ranges
        self.dielectric_value[start_idx:end_idx] = material.epsilon_r
        self.metalic_loss[start_idx:end_idx] = material.metalic_loss
        
        # Pre-calculating loss coefficients for the entire grid
        self.loss_calc1 = (1 - self.metalic_loss) / (1 + self.metalic_loss)
        self.loss_calc2 = 1 / (1 + self.metalic_loss)
        
        # Dynamic Sensor Placement: 20 cells before and after the material
        self.sensor_in_idx = max(50, start_idx - 20)  
        self.sensor_out_idx = min(self.size - 20, end_idx + 20) 
        
        # Document material location for the spatial graph
        self.materials_map.append({
            'start': start_idx, 'end': end_idx,
            'name': material.name, 'is_metal': material.metalic_loss > 0
        })
    
    def physics_engine(self):
        # Step A: Update the magnetic field across the spatial grid
        self.magnetic_field_y[:-1] = self.magnetic_field_y[:-1] + ((self.electric_field_z[1:] - self.electric_field_z[:-1]) / self.imp0)
                
        # Saving boundary values before they are overwritten
        electric_field_z_left_save = self.electric_field_z[1]
        electric_field_z_right_save = self.electric_field_z[-2]

        # Step B: Update the electric field with material coefficients
        self.electric_field_z[1:] = (self.loss_calc1[1:] * self.electric_field_z[1:]) + \
                                    (self.loss_calc2[1:] * ((self.magnetic_field_y[1:] - self.magnetic_field_y[:-1]) * self.imp0 / self.dielectric_value[1:]))
                
        # Applying Absorbing Boundary Conditions (ABC)
        self.electric_field_z[0] = electric_field_z_left_save
        self.electric_field_z[-1] = electric_field_z_right_save

        # Collecting dynamic sensor data
        self.sensor_input.append(self.electric_field_z[self.sensor_in_idx]) 
        self.sensor_output.append(self.electric_field_z[self.sensor_out_idx])

        # Step C: Inject the wave source based on user selection
        if self.source_type == "gaussian":
            self.electric_field_z[50] += np.exp(-0.5 * ((self.time_step - 30.0) / 2.0)**2)
        elif self.source_type == "sine":
            self.electric_field_z[50] += np.sin(2.0 * np.pi * self.time_step / 100.0)

    def step_physics(self):
        # Running the simulation over total time steps for static analysis
        for _ in range(4000):
            self.physics_engine()
            self.time_step += 1

    def run_animation(self):
        # Setting up the live animation plot
        fig, ax = plt.subplots(figsize=(10, 6))
        line, = ax.plot(self.electric_field_z, color='red', label='Electric Field')
        
        # Drawing materials on the background
        for mat in self.materials_map:
            color = 'gray' if mat['is_metal'] else 'green'
            alpha = 0.5 if mat['is_metal'] else 0.3
            ax.axvspan(mat['start'], mat['end'], color=color, alpha=alpha, label=f"Material: {mat['name']}")
            
        ax.set_ylim(-2, 2)
        ax.set_title(f"Wave Propagation Animation ({self.source_type.capitalize()} Source)")
        ax.set_xlabel("Spatial Grid (x)")
        ax.set_ylabel("Amplitude")
        ax.grid(True)
        ax.legend(loc='upper right')

        # Frame update function (runs physics engine in small batches for speed)
        def step(frame):
            for _ in range(3): 
                self.physics_engine()
                self.time_step += 1
            line.set_ydata(self.electric_field_z)
            return line,

        # Global reference to prevent Garbage Collection from stopping the animation
        self.ani = FuncAnimation(fig, step, frames=1500, interval=20, blit=True, repeat=False)
        plt.show()

    def cleancalcs(self):
        # Time gating to clean the input signal from echoes
        self.sensor_input_clean = np.array(self.sensor_input)
        self.sensor_input_clean[150:] = 0 
        
        # Applying Fast Fourier Transform (FFT)
        self.fft_input = np.abs(np.fft.fft(self.sensor_input_clean))
        self.fft_output = np.abs(np.fft.fft(self.sensor_output))
        self.freqs = np.fft.fftfreq(len(self.sensor_input_clean))
        
        # Extracting positive frequencies only
        self.half_len = len(self.freqs) // 2
        self.freqs_positive = self.freqs[:self.half_len]
        self.fft_input_positive = self.fft_input[:self.half_len]
        self.fft_output_positive = self.fft_output[:self.half_len]

    def visualization(self):
        # Engineering Dashboard Setup
        plt.figure(figsize=(12, 12))
        
        # 1. Spatial Domain Snapshot & Setup
        plt.subplot(3, 1, 1)
        plt.plot(self.electric_field_z, color='red', label='Electric Field (Final Snapshot)')
        
        for mat in self.materials_map:
            color = 'gray' if mat['is_metal'] else 'green'
            alpha = 0.5 if mat['is_metal'] else 0.2
            plt.axvspan(mat['start'], mat['end'], color=color, alpha=alpha, label=f"Material: {mat['name']}")
        
        # Dynamic sensor markers
        plt.axvline(self.sensor_in_idx, color='blue', linestyle='--', alpha=0.6, label='Input Sensor')
        plt.axvline(self.sensor_out_idx, color='purple', linestyle='--', alpha=0.6, label='Output Sensor')
        
        plt.title("Spatial Physical Setup & Final Wave State")
        plt.xlabel("Spatial Grid (x)")
        plt.ylabel("Amplitude")
        plt.xlim(0, self.size)
        plt.grid(True)
        plt.legend(loc='upper right', fontsize='small')

        # 2. Frequency Spectrum Graph
        plt.subplot(3, 1, 2)
        plt.plot(self.freqs_positive, self.fft_input_positive, color='blue', label='Pure Input Signal')
        plt.plot(self.freqs_positive, self.fft_output_positive, color='red', label='Transmitted Signal')
        plt.title("Frequency Spectrum (Cleaned from Echoes)")
        plt.ylabel("Magnitude")
        plt.xlim(0, 0.1)
        plt.grid(True)
        plt.legend()

        # 3. S21 Transmission Parameter (dB)
        plt.subplot(3, 1, 3)
        plt.title("S-Parameters: S21 Transmission Coefficient (dB)")
        
        epsilon = 1e-10 # Preventing Math Domain Error (Division by zero)
        fft_input_safe = np.where(self.fft_input_positive < epsilon, epsilon, self.fft_input_positive)
        s21_db = 20 * np.log10(self.fft_output_positive / fft_input_safe)
        
        plt.plot(self.freqs_positive, s21_db, color='purple', linewidth=2, label='S21 (Transmission)')
        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
        plt.xlabel("Normalized Frequency")
        plt.ylabel("Magnitude (dB)")
        plt.xlim(0, 0.1)
        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        plt.show()