import numpy as np
from electricity_prices import price_slots, get_price_slot
from pv_generation import pv_profiles
from scheduling import generate_scheduling, Hyperparameters
from ev_requirements import ev_requirements
import matplotlib.pyplot as plt
import os
from constraints_loader import load_constraints

output_path = './output/'
if not os.path.exists(output_path):
    os.makedirs(output_path)


def shift_value(value):
    """
    Apply a random shift to a given value to simulate variability.
    Ensures the shifted value stays within specified bounds.
    """
    lower_bound = 0
    upper_bound = 2 * value
    std_dev = 0.1 * value
    while True:
        shifted_value = np.random.normal(loc=value, scale=std_dev)
        if lower_bound <= shifted_value <= upper_bound:
            return shifted_value


def generate_solar_profile(period, n_panels):
    """
    Generate a solar energy production profile for a given period and number of panels.
    """
    return {
        hour: n_panels * shift_value(kwh)
        for hour, kwh in pv_profiles[period].items()
    }


def generate_price_slots(period):
    """
    Generate randomized electricity price slots based on existing price data.
    """
    return {
        slot: shift_value(price)
        for slot, price in price_slots[period].items()
    }


def add_ev_constraints(constraints_min, constraints_max, ev_charging_hours, ev_total_energy, ev_power_limit, max_kw):
    """
    Add EV charging constraints to the scheduling constraints.

    Parameters:
        constraints_min: Minimum energy constraints per hour.
        constraints_max: Maximum energy constraints per hour.
        ev_charging_hours: Hours allowed for EV charging.
        ev_total_energy: Total energy required for EV charging.
        ev_power_limit: Maximum charging power per hour.
        max_kw: Global maximum energy allowed per hour.

    Returns:
        Updated minimum and maximum constraints.
    """
    ev_energy_per_hour = ev_total_energy / len(ev_charging_hours)
    for hour in ev_charging_hours:
        constraints_min[hour] = min(constraints_min[hour] + ev_energy_per_hour, max_kw)
        constraints_max[hour] = min(constraints_max[hour] + ev_power_limit, max_kw)

    # Ensure the total EV energy fits within the available maximum constraints
    total_max_available = sum(constraints_max[hour] for hour in ev_charging_hours)
    assert ev_total_energy <= total_max_available, (
        f"EV total energy ({ev_total_energy} kWh) exceeds available maximum constraints ({total_max_available} kWh)"
    )

    return constraints_min, constraints_max


def simulation(weekday, scheduling, pv_panels_count, period, seed=0):
    """
    Simulate energy expenses and energy sold based on scheduling, solar generation, and electricity prices.

    Parameters:
        weekday: Day of the week (0=Monday, ..., 6=Sunday).
        scheduling: Energy scheduling per hour.
        pv_panels_count: Number of solar panels.
        period: Seasonal period (e.g., 'warm', 'cold').
        seed: Random seed for reproducibility.

    Returns:
        Total expenses, total energy sold, and hourly costs.
    """
    np.random.seed(seed)

    tot_expenses = 0
    tot_energy_sold = 0
    hourly_costs = {}
    energy_discount = 0.05

    # Generate solar production and electricity price profiles
    solar_profile = generate_solar_profile(period, n_panels=pv_panels_count)
    price_slots_today = generate_price_slots(period)

    remaining_discounted_energy = 0

    for hour, consumption in scheduling.items():
        # Calculate solar energy and update remaining discounted energy
        energy_generated = solar_profile[hour]
        tot_energy_sold += energy_generated
        remaining_discounted_energy += energy_generated

        # Calculate energy consumption at discounted and full price
        discounted_energy = min(consumption, remaining_discounted_energy)
        full_price_energy = max(0, consumption - discounted_energy)

        remaining_discounted_energy -= discounted_energy

        # Calculate expenses for the hour
        current_price = price_slots_today[get_price_slot(hour, weekday)]
        discounted_price = current_price * energy_discount
        hour_expenses = discounted_price * discounted_energy + current_price * full_price_energy
        tot_expenses += hour_expenses

        # Store hourly cost
        hourly_costs[hour] = hour_expenses

    return tot_expenses, tot_energy_sold, hourly_costs


def grid_search_params(weekday, period, tot_energy, pv_panels_count, constraints_min, constraints_max,
                       hyperparameters_range, hyperparameters_test_count, max_kw, seed=0):
    """
    Perform a grid search to find the optimal hyperparameters for scheduling.

    Parameters:
        weekday: Day of the week.
        period: Seasonal period.
        tot_energy: Total energy to be scheduled.
        pv_panels_count: Number of solar panels.
        constraints_min: Minimum hourly constraints.
        constraints_max: Maximum hourly constraints.
        hyperparameters_range: Range for testing hyperparameters.
        hyperparameters_test_count: Number of test points within the range.
        max_kw: Maximum energy allowed per hour.
        seed: Random seed for reproducibility.

    Returns:
        The best hyperparameters found during the search.
    """
    best_expenses_score = np.inf
    best_hyperparameters = None

    hp_values = np.linspace(hyperparameters_range[0], hyperparameters_range[1], hyperparameters_test_count)

    for hp_morning in hp_values:
        for hp_afternoon in hp_values:
            for hp_evening in hp_values:
                for hp_night in hp_values:
                    hyperparameters = Hyperparameters(hp_morning, hp_afternoon, hp_evening, hp_night)
                    scheduling = generate_scheduling(
                        weekday=weekday,
                        period=period,
                        tot_energy=tot_energy,
                        constraints_min=constraints_min,
                        constraints_max=constraints_max,
                        hyperparameters=hyperparameters,
                        max_kw=max_kw
                    )
                    expenses, _, _ = simulation(
                        weekday=weekday,
                        scheduling=scheduling,
                        pv_panels_count=pv_panels_count,
                        period=period,
                        seed=seed
                    )
                    if expenses < best_expenses_score:
                        best_expenses_score = expenses
                        best_hyperparameters = hyperparameters

    return best_hyperparameters


def plot_scheduling_comparison(initial_scheduling, optimized_scheduling, scenario):
    """
    Plot a comparison of initial and optimized energy scheduling.

    Parameters:
        initial_scheduling: Initial scheduling per hour.
        optimized_scheduling: Optimized scheduling per hour.
        scenario: Description of the scenario (e.g., 'Workdays (Warm)').
    """
    hours = range(24)
    initial_values = [initial_scheduling[hour] for hour in hours]
    optimized_values = [optimized_scheduling[hour] for hour in hours]

    x = np.arange(len(hours))
    bar_width = 0.4

    plt.figure(figsize=(14, 7))
    plt.bar(x - bar_width / 2, initial_values, bar_width, label='Initial Scheduling', color='skyblue', alpha=0.7)
    plt.bar(x + bar_width / 2, optimized_values, bar_width, label='Optimized Scheduling', color='salmon', alpha=0.7)

    plt.xlabel('Hour of the Day')
    plt.ylabel('Energy Scheduled (kWh)')
    plt.title(f'Scheduling Comparison: {scenario}')
    plt.xticks(ticks=x, labels=hours)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'./output/scheduling_comparison_{scenario}.png')
    plt.show()


def plot_hourly_cost_comparison(hourly_costs_initial, hourly_costs_optimized, scenario):
    """
    Plot a comparison of initial and optimized hourly energy costs.

    Parameters:
        hourly_costs_initial: Hourly costs for the initial scheduling.
        hourly_costs_optimized: Hourly costs for the optimized scheduling.
        scenario: Description of the scenario (e.g., 'Workdays (Warm)').
    """
    hours = range(24)
    initial_costs = [hourly_costs_initial.get(hour, 0) for hour in hours]
    optimized_costs = [hourly_costs_optimized.get(hour, 0) for hour in hours]

    x = np.arange(len(hours))
    bar_width = 0.4

    plt.figure(figsize=(14, 7))
    plt.bar(x - bar_width / 2, initial_costs, bar_width, label='Initial Costs (€)', color='skyblue', alpha=0.7)
    plt.bar(x + bar_width / 2, optimized_costs, bar_width, label='Optimized Costs (€)', color='salmon', alpha=0.7)

    plt.xlabel('Hour of the Day')
    plt.ylabel('Cost (€)')
    plt.title(f'Hourly Cost Comparison: {scenario}')
    plt.xticks(ticks=x, labels=hours)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'./output/hourly_cost_comparison_{scenario}.png')
    plt.show()


def plot_results(results):
    """
    Plot a comparison of total expenses across scenarios for initial and optimized scheduling.

    Parameters:
        results: List of dictionaries containing scenario data and expenses.
    """
    scenarios = [r["scenario"] for r in results]
    initial_expenses = [r["initial_expenses"] for r in results]
    optimized_expenses = [r["optimized_expenses"] for r in results]

    plt.figure(figsize=(10, 6))
    bar_width = 0.4
    x = np.arange(len(scenarios))

    plt.bar(x - bar_width / 2, initial_expenses, bar_width, label="Initial Expenses", color="skyblue", alpha=0.7)
    plt.bar(x + bar_width / 2, optimized_expenses, bar_width, label="Optimized Expenses", color="salmon", alpha=0.7)

    plt.xticks(ticks=x, labels=scenarios, rotation=45)
    plt.ylabel("Expenses (€)")
    plt.title("Comparison of Expenses by Scenario")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'./output/total_expences_comparison.png')
    plt.show()


def compare_scenarios(seed=0):
    """
    Compare scheduling and expenses across multiple scenarios (workdays/weekend, warm/cold season).

    Returns:
        List of results containing scheduling, costs, and hyperparameters for each scenario.
    """
    scenarios = [
        {"season": "warm", "day_type": "workdays", "weekday": 4},
        {"season": "warm", "day_type": "weekend", "weekday": 6},
        {"season": "cold", "day_type": "workdays", "weekday": 4},
        {"season": "cold", "day_type": "weekend", "weekday": 6},
    ]

    results = []

    for scenario in scenarios:
        season = scenario["season"]
        day_type = scenario["day_type"]
        weekday = scenario["weekday"]

        print(f"Simulating for {day_type.capitalize()} in {season.capitalize()} season...")

        # Retrieve EV requirements for the current scenario
        ev_config = ev_requirements[day_type]
        ev_total_energy = ev_config["total_energy"]
        ev_charging_hours = ev_config["charging_hours"]
        ev_power_limit = ev_config["power_limit"]

        # Load constraints based on day type
        constraints_min, constraints_max = load_constraints(day_type=day_type, max_kw=6)

        # Add EV constraints to the scheduling
        constraints_min, constraints_max = add_ev_constraints(
            constraints_min, constraints_max, ev_charging_hours, ev_total_energy, ev_power_limit, max_kw=6
        )

        # Set total energy with a margin
        tot_energy = 35 if day_type == "workdays" else 40


        # Generate initial scheduling with default hyperparameters
        default_hyperparameters = Hyperparameters(1, 1, 1, 1)
        initial_scheduling = generate_scheduling(
            weekday=weekday,
            period=season,
            tot_energy=tot_energy,
            constraints_min=constraints_min,
            constraints_max=constraints_max,
            hyperparameters=default_hyperparameters,
            max_kw=6
        )

        # Simulate initial scheduling
        initial_expenses, _, hourly_costs_initial = simulation(
            weekday=weekday,
            scheduling=initial_scheduling,
            pv_panels_count=5,
            period=season,
            seed=seed
        )

        # Perform grid search to find the best hyperparameters
        best_hp = grid_search_params(
            weekday=weekday,
            period=season,
            tot_energy=tot_energy,
            pv_panels_count=5,
            constraints_min=constraints_min,
            constraints_max=constraints_max,
            hyperparameters_range=(0.1, 10),
            hyperparameters_test_count=5,
            max_kw=6,
            seed=seed
        )

        # Generate optimized scheduling
        optimized_scheduling = generate_scheduling(
            weekday=weekday,
            period=season,
            tot_energy=tot_energy,
            constraints_min=constraints_min,
            constraints_max=constraints_max,
            hyperparameters=best_hp,
            max_kw=6
        )

        # Simulate optimized scheduling
        optimized_expenses, _, hourly_costs_optimized = simulation(
            weekday=weekday,
            scheduling=optimized_scheduling,
            pv_panels_count=5,
            period=season,
            seed=seed
        )

        # Store results for the scenario
        results.append({
            "scenario": f"{day_type.capitalize()} ({season.capitalize()})",
            "initial_expenses": initial_expenses,
            "optimized_expenses": optimized_expenses,
            "hourly_costs_initial": hourly_costs_initial,
            "hourly_costs_optimized": hourly_costs_optimized,
            "initial_scheduling": initial_scheduling,
            "optimized_scheduling": optimized_scheduling,
            "best_hyperparameters": best_hp,
            "constraints_min": constraints_min,
            "constraints_max": constraints_max
        })

    return results



def plot_scheduling(scheduling, constraints_min, constraints_max):
    dayhours = list(range(0, 24))
    plt.fill_between(dayhours, 0, constraints_min.values(), step='pre', color='blue', alpha=0.2,
                     label='User preferences (min)')
    plt.fill_between(dayhours, constraints_min.values(), scheduling.values(), step='pre', color='green', alpha=0.2,
                     label='Scheduling')
    plt.step(dayhours, constraints_max.values(), color='red', label='User preferences (max)')
    plt.legend(framealpha=0.5)
    plt.show()


def main():

    """
    Main function to simulate, compare, and visualize results for various scenarios.
    """
    results = compare_scenarios(seed=42)

    for result in results:
        print(f"Scenario: {result['scenario']}")
        print("Initial Expenses:", result["initial_expenses"])
        print("Optimized Expenses:", result["optimized_expenses"])
        print("Best Hyperparameters:")
        print(f"  Morning: {result['best_hyperparameters'].morning}")
        print(f"  Afternoon: {result['best_hyperparameters'].afternoon}")
        print(f"  Evening: {result['best_hyperparameters'].evening}")
        print(f"  Night: {result['best_hyperparameters'].night}")

        # Plot scheduling comparison for the scenario
        plot_scheduling_comparison(
            initial_scheduling=result["initial_scheduling"],
            optimized_scheduling=result["optimized_scheduling"],
            scenario=result["scenario"]
        )

        # Plot hourly cost comparison for the scenario
        plot_hourly_cost_comparison(
            hourly_costs_initial=result["hourly_costs_initial"],
            hourly_costs_optimized=result["hourly_costs_optimized"],
            scenario=result["scenario"]
        )

        plot_scheduling(result['optimized_scheduling'], result['constraints_min'], result['constraints_max'])
    # Plot overall results for all scenarios
    plot_results(results)


if __name__ == "__main__":
    main()
