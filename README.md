# SmartGrids_project – Home Energy Management System

This project, developed as part of the *ICT for Smart Societies* course, focuses on designing and simulating a **Home Energy Management System (HEMS)** that optimizes energy consumption based on photovoltaic (PV) generation, dynamic electricity pricing, and electric vehicle (EV) charging needs.

## ⚙️ Key Concepts

- **Prosumer Modeling**: A household equipped with solar panels and an EV is modeled to simulate realistic energy demands and constraints.
- **Energy Scheduling Optimization**: The system generates a cost-effective schedule for daily energy consumption while respecting hourly energy limits, user preferences, and total energy demand.
- **Mathematical Modeling**: A multi-criteria objective function and constraint-based optimizer are applied to schedule energy usage.
- **Optimization Strategy**: A grid search over hyperparameters is performed to minimize energy cost across different scenarios (workdays/weekends, cold/warm conditions).

## 📈 Results

The optimized schedule demonstrates:
- Up to **23.6% cost savings** on specific days
- Flexibility in adapting to different climate and usage scenarios
- Integration of real-world PV data and national electricity prices (PUN)

## 📁 Repository Structure

- `Project/` – Python source code and simulation scripts
- `Report.pdf` – Detailed project report including methodology, pseudocode, and results

