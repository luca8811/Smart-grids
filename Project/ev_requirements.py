# EV requirements for charging
ev_requirements = {
    "workdays": {
        "total_energy": 10,  # Total energy required per day (kWh)
        "charging_hours": list(range(22, 24)) + list(range(0, 6)),  # 22:00 - 06:00
        "power_limit": 3.6,  # Maximum charging power (kW)
    },
    "weekend": {
        "total_energy": 15,  # Total energy required per day (kWh)
        "charging_hours": list(range(20, 24)) + list(range(0, 8)),  # 20:00 - 08:00
        "power_limit": 3.6,  # Maximum charging power (kW)
    },
}
