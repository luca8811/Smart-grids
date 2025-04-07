from pv_generation import pv_profiles
from electricity_prices import get_price_slot, get_price_slots_scores


class Hyperparameters:
    def __init__(self, morning: float, afternoon: float, evening: float, night: float):
        self.morning = morning
        self.afternoon = afternoon
        self.evening = evening
        self.night = night


def build_hp_factors(hyperparameters: Hyperparameters):
    """
    Build hourly weighting factors based on the provided hyperparameters.
    """
    factors = {}

    # Assign factors for morning hours (7 AM - 12 PM)
    for hour in range(7, 13):
        factors[hour] = hyperparameters.morning

    # Assign factors for afternoon hours (1 PM - 6 PM)
    for hour in range(13, 19):
        factors[hour] = hyperparameters.afternoon

    # Assign factors for evening hours (7 PM - 10 PM)
    for hour in range(19, 23):
        factors[hour] = hyperparameters.evening

    # Assign factors for night hours (11 PM - 6 AM)
    for hour in range(23, 31):
        factors[hour % 24] = hyperparameters.night

    return factors


def compute_pv_factors(pv_profile):
    """
    Compute normalized PV generation factors for each hour.
    """
    pv_min = min(pv_profile.values())
    pv_max = max(pv_profile.values())

    # Normalize PV factors to a range of [0, 1]
    return {
        hour: (pv_profile[hour] - pv_min) / (pv_max - pv_min)
        for hour in pv_profile.keys()
    }


def evaluate_goodness(current_scheduling, max_scheduling, price_slot_score, pv_factor, hp_factor):
    """
    Evaluate the goodness of scheduling based on current usage, price, and other factors.
    """
    return (1 - (current_scheduling / max_scheduling) ** 2) * (price_slot_score / 2 + pv_factor + hp_factor)


def generate_scheduling(weekday, period, tot_energy, constraints_min, constraints_max,
                        hyperparameters, max_kw=3):
    """
    Generate an energy scheduling plan based on constraints and optimization factors.

    Parameters:
        - weekday: Day of the week.
        - period: Time period for the PV profile.
        - tot_energy: Total energy to be scheduled.
        - constraints_min: Minimum energy constraints for each hour.
        - constraints_max: Maximum energy constraints for each hour.
        - hyperparameters: Hyperparameters object with weighting factors.
        - max_kw: Maximum energy allowed per hour.

    Returns:
        - A dictionary with the energy scheduling for each hour.
    """
    # Validate constraints
    dayhours = list(range(0, 24))
    assert list(constraints_min.keys()) == dayhours
    assert all(value >= 0 for value in constraints_min.values())
    assert all(value <= max_kw for value in constraints_max.values())
    assert sum(constraints_min.values()) <= tot_energy
    assert sum(constraints_max.values()) >= tot_energy

    # Load PV profile and compute factors
    pv_profile = pv_profiles[period]
    pv_factors = compute_pv_factors(pv_profile)
    hp_factors = build_hp_factors(hyperparameters)
    price_slots_score = get_price_slots_scores(period)

    # Initialize scheduling and remaining energy
    scheduling = {hour: 0 for hour in dayhours}
    remaining_energy = tot_energy

    # Apply minimum consumption constraints
    for hour in dayhours:
        remaining_energy -= constraints_min[hour]
        scheduling[hour] += constraints_min[hour]

    # Distribute remaining energy
    while remaining_energy > 0.0001:
        # Calculate goodness factors for each hour
        goodness_factors = {
            hour: evaluate_goodness(
                scheduling[hour],
                max_kw,
                price_slots_score.index(get_price_slot(hour, weekday)),
                pv_factors[hour],
                hp_factors[hour]
            )
            for hour in dayhours
        }

        # Normalize goodness factors so that sum(goodness_factors) = 1
        normalization_value = sum(goodness_factors.values())
        goodness_factors_norm = {hour: goodness_factors[hour] / normalization_value for hour in dayhours}

        # Calculating how much energy should be assigned to each dayhour
        energy_assignments = {hour: remaining_energy * goodness_factors_norm[hour] for hour in dayhours}

        for hour in dayhours:
            # Calculate energy to assign based on goodness proportion
            # energy_proportion = goodness_factors[hour] / normalization_value
            # energy_to_assign = remaining_energy * energy_proportion
            energy_to_assign = energy_assignments[hour]

            # Apply constraints and assign energy
            max_energy = min(max_kw, constraints_max[hour])
            energy_assigned = min(energy_to_assign, max_energy - scheduling[hour])

            scheduling[hour] += energy_assigned
            remaining_energy -= energy_assigned

    return scheduling
