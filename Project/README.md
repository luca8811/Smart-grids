# Home Energy Management System

This project simulates energy scheduling, incorporating solar photovoltaic (PV) generation, electricity prices influenced by grid demand, and electric vehicle (EV) charging requirements. The goal is to minimize costs while adhering to constraints like maximum energy consumption and EV charging needs.

---

## Features

- Hourly energy scheduling for different scenarios (warm/cold seasons, workdays/weekends).
- Incorporation of PV generation profiles and electricity pricing, which considers grid demand patterns.
- Optimization using hyperparameters for better energy distribution.
- Visualization of results with comparison plots.

---

## Prerequisites

Before running the simulation, ensure the following are installed:

- Python (>=3.8)
- `pip` for managing Python packages

---

## Setup Instructions

### 1. Extract the ZIP File

Download and extract the provided `.zip` file to your desired directory. 

### 2. Create a Virtual Environment (Recommended)

Set up a Python virtual environment to keep dependencies isolated:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
### 3. Install Dependencies

After activating the virtual environment, navigate to the extracted folder and install the required libraries:

```bash
pip install numpy matplotlib
```
These dependencies are essential for:

- numpy: Performing numerical computations.
- matplotlib: Creating visualizations for the simulation results.

---

## Run the Simulation
To run the simulation, execute the simulation.py file in your terminal. Make sure your terminal is inside the project directory and the virtual environment is active:
```bash
python simulation.py
```

The script will run simulations for different scenarios (before and after optimization) and generate outputs and plots, which will be saved in the `output/` directory.

---

## Understand the Files
- `simulation.py`: The main script for running energy scheduling simulations.
- `electricity_prices.py`: Models electricity prices influenced by grid demand patterns.
- `ev_requirements.py`: Contains EV charging constraints like total energy required, charging hours, and power limits.
- `pv_generation.py`: Models PV generation profiles for different seasons and periods.
- `scheduling.py`: Implements the scheduling algorithm, incorporating PV generation, price factors, and user-defined constraints to optimize energy distribution throughout the day.
- `constraints_loader.py`: Dynamically loads user-defined minimum and maximum energy constraints for each hour from a `constraints.json` file.


#### Modifying Constraints
- Edit the `constraints.json` file to adjust minimum and maximum energy constraints for each hour.
- Example format for `constraints.json`:
```json
{
    "min": {
        "0": 0.5,
        "1": 0.5,
        "2": 0.5,
        "...": "..."
    },
    "max": {
        "0": 3,
        "1": 3,
        "2": 3,
        "...": "..."
    }
}

```
Note: ``"...": "..."`` indicates repetition for all 24 hours.
- It is used "min": 0.5 or "max": 3 as shortcuts to apply uniform constraints for all hours.

---

## View the Results

After running the simulation, the console will display:

- **Progress Updates**: Details of the simulation progress for each scenario (e.g., *Simulating for Workdays in Warm season*).
- **Initial and Optimized Expenses**: A breakdown of energy costs before and after optimization for each scenario.
- **Best Hyperparameters**: The optimal values for morning, afternoon, evening, and night energy scheduling preferences.
- **Generated Plots**:
  - **Energy Scheduling Comparison**: Initial vs. Optimized energy scheduling for each scenario.
  - **Hourly Energy Cost Comparison**: Initial vs. Optimized hourly costs for each scenario.
  - **Energy Scheduling vs. User-Defined Constraints**: A comparison of optimized scheduling with user-defined minimum and maximum constraints for each scenario.
  - **Total Expenses by Scenario**: Comparison of total costs (initial and optimized) across all scenarios.


