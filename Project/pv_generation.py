import matplotlib.pyplot as plt

pv_profiles = {
    'summer': {0: 0.001,
               1: 0.001,
               2: 0.001,
               3: 0.001,
               4: 0.001,
               5: 0.03,
               6: 0.125,
               7: 0.27,
               8: 0.42,
               9: 0.575,
               10: 0.69,
               11: 0.74,
               12: 0.75,
               13: 0.71,
               14: 0.64,
               15: 0.55,
               16: 0.41,
               17: 0.27,
               18: 0.15,
               19: 0.05,
               20: 0.005,
               21: 0.001,
               22: 0.001,
               23: 0.001},
    'spring': {0: 0.001,
               1: 0.001,
               2: 0.001,
               3: 0.001,
               4: 0.001,
               5: 0.01,
               6: 0.07,
               7: 0.17,
               8: 0.32,
               9: 0.45,
               10: 0.565,
               11: 0.63,
               12: 0.65,
               13: 0.6,
               14: 0.54,
               15: 0.44,
               16: 0.31,
               17: 0.18,
               18: 0.07,
               19: 0.02,
               20: 0.001,
               21: 0.001,
               22: 0.001,
               23: 0.001},
    'autumn': {0: 0.001,
               1: 0.001,
               2: 0.001,
               3: 0.001,
               4: 0.001,
               5: 0.001,
               6: 0.01,
               7: 0.07,
               8: 0.19,
               9: 0.32,
               10: 0.415,
               11: 0.47,
               12: 0.49,
               13: 0.44,
               14: 0.365,
               15: 0.275,
               16: 0.15,
               17: 0.05,
               18: 0.02,
               19: 0.001,
               20: 0.001,
               21: 0.001,
               22: 0.001,
               23: 0.001},
    'winter': {0: 0.001,
               1: 0.001,
               2: 0.001,
               3: 0.001,
               4: 0.001,
               5: 0.001,
               6: 0.001,
               7: 0.001,
               8: 0.04,
               9: 0.14,
               10: 0.25,
               11: 0.315,
               12: 0.34,
               13: 0.31,
               14: 0.26,
               15: 0.17,
               16: 0.08,
               17: 0.025,
               18: 0.001,
               19: 0.001,
               20: 0.001,
               21: 0.001,
               22: 0.001,
               23: 0.001},
}

pv_profiles['warm'] = {dh: (pv_profiles['spring'][dh] + pv_profiles['summer'][dh]) / 2
                       for dh in range(24)}
pv_profiles['cold'] = {dh: (pv_profiles['autumn'][dh] + pv_profiles['winter'][dh]) / 2
                       for dh in range(24)}
# seasons = ['summer', 'spring', 'autumn', 'winter']
# for s in seasons:
#     pv_profiles.pop(s)

if __name__ == '__main__':
    seasons_colors = {'summer': 'gold', 'spring': 'green', 'autumn': 'darkorange', 'winter': 'blue'}
    periods_colors = {'warm': 'gold', 'cold': 'blue'}
    fig, ax = plt.subplots(1, 2, figsize=(15, 8))
    fig.suptitle('Hourly avg kWh electricity output per kW of solar PV (Turin)')

    # Seasons
    for season in seasons_colors.keys():
        ax[0].step(pv_profiles[season].keys(), pv_profiles[season].values(), label=season, color=seasons_colors[season])
    ax[0].set_xticks(list(range(0, 24)))
    ax[0].set_ylim((-0.05, 0.8))
    ax[0].set_xlabel('Time (h)')
    ax[0].set_ylabel('Average kWh')
    ax[0].legend()
    ax[0].grid()

    # Periods
    for period in periods_colors.keys():
        ax[1].step(pv_profiles[period].keys(), pv_profiles[period].values(), label=period, color=periods_colors[period])
    ax[1].set_xticks(list(range(0, 24)))
    ax[1].set_ylim((-0.05, 0.8))
    ax[1].set_xlabel('Time (h)')
    ax[1].set_ylabel('Average kWh')
    ax[1].legend()
    ax[1].grid()

    # Showing
    plt.tight_layout()
    plt.show()
