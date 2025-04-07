import json
import numbers

CONSTRAINTS_FILE = 'constraints.json'

def parse_constraints(constraints, max_kw):
    dayhours = list(range(24))
    constraints_min = {hour: 0 for hour in dayhours}
    constraints_max = {hour: max_kw for hour in dayhours}

    for period, values in constraints.items():
        start, end = map(float, period.split('-'))
        start_hour = int(start)
        end_hour = int(end if end != 24 else 0)

        if start < end:
            hours = list(range(start_hour, end_hour))
        else:
            hours = list(range(start_hour, 24)) + list(range(0, end_hour))

        for hour in hours:
            constraints_min[hour] = values['min']
            constraints_max[hour] = values['max']

    return constraints_min, constraints_max

def load_constraints(day_type, max_kw):
    with open(CONSTRAINTS_FILE, 'r') as f:
        constraints_data = json.load(f)

    if day_type not in constraints_data:
        raise ValueError(f"Day type '{day_type}' not found in constraints file.")

    return parse_constraints(constraints_data[day_type], max_kw)
