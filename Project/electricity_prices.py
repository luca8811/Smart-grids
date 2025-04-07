import matplotlib.pyplot as plt
import os

output_path = './output/'
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Values are in €/kWh
price_slots = {
    'warm': {
        1: 0.106118333,
        2: 0.12321,
        3: 0.099136667
    },
    'cold': {
        1: 0.121395,
        2: 0.117425,
        3: 0.097566667
    }
}


def get_price_slots_scores(period):
    return sorted(price_slots[period].keys(), key=lambda x: price_slots[period][x], reverse=True)


def get_price_slot(dayhour, weekday):
    """
    :param dayhour: hour of the day [0, 24)
    :param weekday: day of the week [0, 6]
    :return: time slot
    """
    assert 0 <= dayhour < 24 and 0 <= weekday < 7 and isinstance(weekday, int)
    # First time slot
    if weekday <= 4 and 7 <= dayhour < 19:
        return 1
    # Second time slot
    if weekday <= 5 and 6 <= dayhour < 23:
        return 2
    # Third time slot
    return 3


if __name__ == '__main__':
    # Display electricity prices for each slot in the warm and cold periods
    print("Electricity prices for warm period:")
    for slot, price in price_slots['warm'].items():
        print(f"Slot {slot}: {price:.6f} €/kWh")

    print("\nElectricity prices for cold period:")
    for slot, price in price_slots['cold'].items():
        print(f"Slot {slot}: {price:.6f} €/kWh")

    # Plot electricity prices
    warm_prices = list(price_slots['warm'].values())
    cold_prices = list(price_slots['cold'].values())
    slots = list(price_slots['warm'].keys())  # Assuming same slots for warm and cold

    plt.figure(figsize=(8, 5))
    plt.bar([slot - 0.2 for slot in slots], warm_prices, width=0.4, label='Warm Period', color='gold', alpha=0.7)
    plt.bar([slot + 0.2 for slot in slots], cold_prices, width=0.4, label='Cold Period', color='blue', alpha=0.7)

    plt.xlabel("Time Slots")
    plt.ylabel("Electricity Price (€/kWh)")
    plt.title("Electricity Prices for Warm and Cold Periods")
    plt.xticks(ticks=slots, labels=[f"Slot {slot}" for slot in slots])
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("./output/electricity_prices.png", dpi=300)
    plt.show()
