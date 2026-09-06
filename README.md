# FDTD-RF-Simulator
A professional-grade, Object-Oriented Python engineering tool for simulating electromagnetic wave propagation, material interaction, and frequency-domain analysis using the Finite-Difference Time-Domain (FDTD) Yee algorithm.

This project bridges theoretical electromagnetics (Maxwell's equations) and algorithmic software development to create a lightweight Electronic Design Automation (EDA) tool. It is designed to model how RF signals behave when encountering different media, extracting critical hardware design metrics like S-Parameters.

Key Features
FDTD Physics Engine: Implements the 1D Yee algorithm for updating Electric (E) and Magnetic (H) fields over a spatial grid. Optimized for computational speed by replacing iterative loops with NumPy vectorized array operations.

Absorbing Boundary Conditions (ABC): Eliminates artificial reflections at the grid edges, accurately simulating open-space wave propagation.

Dynamic Sensor Architecture: Sensors automatically adjust their positions based on the user's custom material placement, ensuring accurate input (reference) and output (transmitted) wave sampling.

Digital Signal Processing (DSP): Uses a broadband Gaussian pulse paired with Time-Gating to eliminate echo interference. Applies Fast Fourier Transform (FFT) to extract the frequency response across the spectrum.

S-Parameter Extraction (S21): Automatically calculates and normalizes transmission coefficients into the decibel (dB) scale, allowing for precise measurement of signal attenuation and material shielding effectiveness.

Event-Driven GUI: A custom Tkinter frontend featuring interactive material placement, dielectric/conductor configuration, and real-time animation versus static analysis modes.

Repository Structure
The project follows a modular software architecture:

FDTD-RF-Simulator/
├── main.py             # The core physics engine and Tkinter GUI
├── requirements.txt    # Project dependencies
├── .gitignore          # Git exclusion rules
└── assets/             # Directory for screenshots and documentation visuals

Installation & Usage
Clone the repository:
git clone https://github.com/avivmostytskyywork/FDTD-RF-Simulator.git
cd FDTD-RF-Simulator

Install dependencies:
pip install -r requirements.txt

Run the Simulator:
python main.py

Workflow:

Select a predefined material (Glass/Copper) or create a Custom Material (epsilon_r and metallic loss).

Define the spatial bounds (Start Index and Width) for the material in the simulation grid.

Choose between Static Analysis (generates S-Parameter engineering graphs) or Live Animation (visualizes the time-domain wave propagation).

Dashboards & Visuals
Engineering Analysis Dashboard
Displays the final spatial wave state, the cleaned frequency spectrum, and the S21 transmission coefficient (dB) highlighting material attenuation.

Simulation Setup GUI
Event-driven configuration wizard for material properties and testbench bounds.

Engineering & Academic Context
This project was developed as a portfolio asset for hardware and firmware engineering. It synthesizes core concepts from the Computer Engineering (Hardware Track) curriculum at Bar-Ilan University—specifically bridging theoretical concepts from Physics 2 with the practical efficiency of Data Structures, Algorithms, and Object-Oriented Python.

By managing memory allocations efficiently with NumPy and structuring the state management cleanly, it demonstrates the intersection of software engineering and physical hardware design.

Tech Stack
Language: Python

Computation & Math: NumPy, SciPy (FFT)

Data Visualization: Matplotlib (Static plots & FuncAnimation)

Graphical User Interface: Tkinter
