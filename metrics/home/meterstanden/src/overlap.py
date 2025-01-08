import datetime
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md


# from pandas.plotting import register_matplotlib_converters
# register_matplotlib_converters()

HERE = Path(__file__).parent

fn = HERE.parent / "data" / "meterstanden.csv"

df = pd.read_csv(fn, comment='#')

df['time'] = pd.to_datetime(df['Date_Time'], format='%Y-%m-%d %H:%M')
df['month'] = pd.to_datetime(df['time'].dt.month, format='%m')
df['year'] = df['time'].dt.year
df['doy'] = df['time'].dt.dayofyear

df = df[['year', 'doy', 'Gas', 'eDag', 'Water']]
df = df.dropna()

day_afrekening = int(datetime.datetime(2022, 4, 1, 0, 0, 0, 0).strftime("%j"))

# offset for day of year

doy_280 = datetime.datetime(2022, 10, 7, 0, 0, 0, 0).strftime("%j")
doy_226 = datetime.datetime(2022, 8, 14, 0, 0, 0, 0).strftime("%j")
doy_027 = datetime.datetime(2022, 1, 27, 0, 0, 0, 0).strftime("%j")

# -------------------- Make the plot for Gas ---------------------------------------------------------------------------

offset_gas_280 = {2015: 0.288, 2016: 1664.936, 2017: 3936.008, 2019: 8700.027, 2022: 19096.456}
offset_gas_226 = {2016: 1587.984, 2017: 3846.380, 2018: 5533.090, 2019: 8453.316, 2022: 19032.746}
offset_gas_027 = {2016: 688, 2017: 2780, 2018: 4700, 2019: 7220, 2020: 10500, 2021: 14032, 2022: 17745}
offset_gas_003 = {2016: 499, 2017: 2438, 2018: 4535, 2019: 6744, 2020: 10102, 2021: 13511, 2022: 17247, 2023: 19971, 2024: 22525, 2025: 25545}

offsets = offset_gas_003  # Offset on 3rd January

# 110.x DPI -> 1440 Pixels = 13"
# 130.x DPI -> 1680 Pixels = 13"
# 147.x DPI -> 1920 Pixels = 13"

fig, (ax_gas, ax_edag, ax_h2o) = plt.subplots(3, 1, sharex=True, figsize=(7, 7), dpi=130, layout='tight')

# for year in offsets:
for year in [2022, 2023, 2024, 2025]:
    x = df[df['year'] == year]['doy']
    y = df[df['year'] == year]['Gas']
    ax_gas.scatter(x, y-offsets[year], label=year, s=4)

ax_gas.axvline(day_afrekening, linewidth=1)

ax_gas.set_ylabel("m$^3$")
ax_gas.set_title("Jaarlijks Gasverbruik")
ax_gas.legend()

# -------------------- Make the plot for electricity -------------------------------------------------------------------

offset_edag_027 = {2016: 164082, 2017: 167001, 2018: 169195, 2019: 168437, 2020: 168600, 2021: 168812, 2022: 170393}
offset_edag_003 = {2016: 163695, 2017: 166632, 2018: 168820, 2019: 168041, 2020: 168317, 2021: 168206, 2022: 169785, 2023: 168525, 2024: 167878, 2025: 167929}

offsets = offset_edag_003  # Offset on 3rd January

# for year in offsets:
for year in [2022, 2023, 2024, 2025]:
    x = df[df['year'] == year]['doy']
    y = df[df['year'] == year]['eDag']
    ax_edag.scatter(x, y-offsets[year], label=year, s=4)

ax_edag.axvline(day_afrekening, linewidth=1)

ax_edag.set_ylabel("kWh")
ax_edag.set_title("Jaarlijks Elektriciteitsverbruik")
ax_edag.legend()

# -------------------- Make the plot for water -------------------------------------------------------------------------

offset_h2o_003 = {2020: 1152, 2021: 1340, 2022: 1515, 2023: 1667, 2024: 1818, 2025: 1984}

offsets = offset_h2o_003  # Offset on 3rd January

# for year in offsets:
for year in [2022, 2023, 2024, 2025]:
    x = df[df['year'] == year]['doy']
    y = df[df['year'] == year]['Water']
    ax_h2o.scatter(x, y-offsets[year], label=year, s=4)

ax_h2o.axvline(day_afrekening, linewidth=1)

ax_h2o.set_ylabel("m$^3$")
ax_h2o.set_title("Jaarlijks Waterverbruik")
ax_h2o.legend()

plt.show()
