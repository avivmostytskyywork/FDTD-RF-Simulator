import tkinter as tk
from tkinter import messagebox

# ייבוא הליבה הפיזיקלית מתוך הקובץ שיצרנו
from fdtd_engine import Material, FDTDSimulator

# ==========================================
# Graphical User Interface (GUI)
# ==========================================
class SimulationMenu:
    def __init__(self):
        # Setting up the Main Canvas
        self.root = tk.Tk()
        self.root.title("FDTD RF Simulator")
        self.root.geometry("450x400")
        self.root.configure(bg="#2b2b2b")
        
        title = tk.Label(self.root, text="Select Simulation Mode", font=("Arial", 18, "bold"), bg="#2b2b2b", fg="white")
        title.pack(pady=30)

        # Main Menu Buttons
        tk.Button(self.root, text="1. Glass Dielectric (er=2.5)", font=("Arial", 14), width=25, bg="#4CAF50", fg="white", command=self.run_glass).pack(pady=10)
        tk.Button(self.root, text="2. Copper Metal (High Loss)", font=("Arial", 14), width=25, bg="#FF5722", fg="white", command=self.run_copper).pack(pady=10)
        tk.Button(self.root, text="3. Custom Material", font=("Arial", 14), width=25, bg="#0084FF", fg="white", command=self.run_custom).pack(pady=10)
        tk.Button(self.root, text="Exit", font=("Arial", 14), width=25, bg="#607D8B", fg="white", command=self.root.destroy).pack(pady=30)

    # Pre-defined Materials
    def run_glass(self):
        self.open_placement_popup(Material(name="Glass", epsilon_r=2.5, metalic_loss=0.0))

    def run_copper(self):
        self.open_placement_popup(Material(name="Copper", epsilon_r=1.0, metalic_loss=1.5))
    
    # Custom Material Creation Wizard
    def run_custom(self):
        popup = tk.Toplevel(self.root)
        popup.title("Custom Material Settings")
        popup.geometry("300x350")
        popup.configure(bg="#2b2b2b")

        # Input fields for physics variables
        tk.Label(popup, text="Material Name:", font=("Arial", 12), bg="#2b2b2b", fg="white").pack(pady=(20, 5))
        entry_name = tk.Entry(popup, font=("Arial", 12), justify="center")
        entry_name.pack(pady=5); entry_name.insert(0, "MyMaterial")

        tk.Label(popup, text="Epsilon_r (e.g., 2.5):", font=("Arial", 12), bg="#2b2b2b", fg="white").pack(pady=(10, 5))
        entry_eps = tk.Entry(popup, font=("Arial", 12), justify="center")
        entry_eps.pack(pady=5); entry_eps.insert(0, "1.0")

        tk.Label(popup, text="Metalic Loss (e.g., 0.0):", font=("Arial", 12), bg="#2b2b2b", fg="white").pack(pady=(10, 5))
        entry_loss = tk.Entry(popup, font=("Arial", 12), justify="center")
        entry_loss.pack(pady=5); entry_loss.insert(0, "0.0")

        def proceed():
            # Try-Except block to prevent crashes from bad user input
            try:
                eps = float(entry_eps.get())
                loss = float(entry_loss.get())
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers for Epsilon and Loss.", parent=popup)
                return
                
            mat = Material(name=entry_name.get(), epsilon_r=eps, metalic_loss=loss)
            popup.destroy()
            self.open_placement_popup(mat) 

        tk.Button(popup, text="Next: Placement", font=("Arial", 12, "bold"), bg="#0084FF", fg="white", command=proceed).pack(pady=25)

    # Material Placement & Simulation Execution Wizard
    def open_placement_popup(self, selected_material):
        popup = tk.Toplevel(self.root)
        popup.title(f"Simulation Settings: {selected_material.name}")
        popup.geometry("380x420") 
        popup.configure(bg="#2b2b2b")

        tk.Label(popup, text=f"Settings for: {selected_material.name}", font=("Arial", 14, "bold"), bg="#2b2b2b", fg="#4CAF50").pack(pady=10)

        # Placement Settings Options
        tk.Label(popup, text="Start Position (Index):", font=("Arial", 11), bg="#2b2b2b", fg="white").pack()
        entry_start = tk.Entry(popup, font=("Arial", 11), justify="center"); entry_start.pack(); entry_start.insert(0, "250")
        tk.Label(popup, text="Material Width (Cells):", font=("Arial", 11), bg="#2b2b2b", fg="white").pack(pady=(10,0))
        entry_width = tk.Entry(popup, font=("Arial", 11), justify="center"); entry_width.pack(); entry_width.insert(0, "50")

        tk.Frame(popup, height=2, bd=1, relief="sunken", bg="gray").pack(fill="x", padx=20, pady=15)

        # Output Mode Selection (Radio Buttons)
        tk.Label(popup, text="Select Output Mode:", font=("Arial", 12, "bold"), bg="#2b2b2b", fg="white").pack()
        
        output_mode = tk.StringVar(value="results") # Default to engineering graphs
        
        tk.Radiobutton(popup, text="Static Analysis (Graphs & S-Parameters)", variable=output_mode, value="results", bg="#2b2b2b", fg="white", selectcolor="black").pack(anchor="w", padx=40, pady=2)
        tk.Radiobutton(popup, text="Animation (Momentary Gaussian Pulse)", variable=output_mode, value="anim_gaussian", bg="#2b2b2b", fg="white", selectcolor="black").pack(anchor="w", padx=40, pady=2)
        tk.Radiobutton(popup, text="Animation (Continuous Sine Wave)", variable=output_mode, value="anim_sine", bg="#2b2b2b", fg="white", selectcolor="black").pack(anchor="w", padx=40, pady=2)

        def submit_and_run():
            # Validation Step 1: Ensure integers are provided
            try:
                start_idx = int(entry_start.get())
                width = int(entry_width.get())
            except ValueError:
                messagebox.showerror("Error", "Enter integers only.", parent=popup)
                return

            MAX_SIZE = 500
            end_idx = start_idx + width
            
            # Validation Step 2: Ensure material stays within grid bounds
            if start_idx < 0 or width <= 0 or end_idx > MAX_SIZE:
                messagebox.showerror("Error", "Invalid placement bounds.", parent=popup)
                return

            mode = output_mode.get()
            popup.destroy()
            
            # Route logic based on mode selection
            if mode == "anim_sine":
                source = "sine"
            else:
                source = "gaussian"

            # Initialize FDTD Engine and run
            sim = FDTDSimulator(size=MAX_SIZE, source_type=source)
            sim.add_material(start_idx=start_idx, end_idx=end_idx, material=selected_material)
            
            if mode == "results":
                sim.step_physics()
                sim.cleancalcs()
                sim.visualization()
            else:
                sim.run_animation()

        tk.Button(popup, text="Run Simulation", font=("Arial", 12, "bold"), bg="#E91E63", fg="white", command=submit_and_run).pack(pady=20)

    def show(self):
        # Keeps the Tkinter window alive and waiting for events
        self.root.mainloop()

# ==========================================
# Main Execution
# ==========================================
if __name__ == "__main__":
    menu = SimulationMenu()
    menu.show()