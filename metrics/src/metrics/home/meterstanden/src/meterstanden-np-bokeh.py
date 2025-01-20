try:
    import bokeh as bk
    import pandas as pd
except ImportError:
    print("This script requires Bokeh and Pandas.")
    raise

import numpy as np
import os

from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file, save
from bokeh.models import HoverTool, ColumnDataSource, LabelSet
from datetime import datetime

output_notebook()

datadir = os.path.expanduser('~/Git/Pythonista/Meterstanden')
outputdir = os.path.expanduser('~/Private/Dropbox/Documents/Meterstanden')
filename = os.path.join(datadir, 'Meterstanden.csv')

# The values below match the iPhone 7 or iPad Pro display

plot_width  = 1334   # iPhone 7 width
plot_height = 750    # iPhone 7 height

plot_width  = int(2048 / 2)  # iPad Pro 9.7" logical width
plot_height = int(1536 / 2)  # iPad Pro 9.7" logical height

print (type(plot_width))
print (type(plot_height))


# The browser to start when run om my Macbook Pro [safari, firefox, chrome]

show_browser = "safari"



# Load the data from the csv file 

data = np.recfromcsv(filename)



# Convert the byte string b'' into a 'normal' string

dt = [datetime.strptime(x.decode('UTF-8'), '%Y-%m-%d %H:%M') for x in data['date_time']]




# Maak een plot voor het waterverbruik

p = figure(x_axis_label='Datum', x_axis_type='datetime', y_axis_label='Volume (m^3)', \
           plot_height=plot_height, plot_width=plot_width, title='Verbruik Water')

p.circle(dt, data['water'])

output_file(os.path.join(outputdir, "Verbruik_Water.html"))
save(p)
show(p, browser=show_browser)





# Maak een plot voor het gasverbruik

p = figure(x_axis_label='Datum', x_axis_type='datetime', y_axis_label='Volume (m^3)', \
           plot_height=plot_height, plot_width=plot_width, title='Verbruik Gas')

p.circle(dt, data['gas'])

output_file(os.path.join(outputdir, "Verbruik_Gas.html"))
save(p)
show(p, browser=show_browser)





# Maak een plot voor het gasverbruik per dag

# Bereken het verbruik in gas tussen twee opeenvolgende metingen

g1 = data['gas'][0:-1]
g2 = data['gas'][1:]
g_diff = np.array(g2-g1)

# Bereken de tijd tussen twee opeenvolgende metingen in dagen

d1 = dt[0:-1]
d2 = dt[1:]

helper = np.vectorize(lambda x: x.total_seconds())
dt_sec = helper(np.array(d2)-np.array(d1))
dt_days = dt_sec / 60. / 60. / 24.





# Bereken het verbruik van gas per dag

gpd = g_diff / dt_days


from bokeh.models import LinearAxis, Range1d

p = figure(x_axis_label='Datum', x_axis_type='datetime', y_axis_label='Verbruik (m^3/dag)', \
           plot_height=plot_height, plot_width=plot_width, title='Verbruik Gas per dag')

p.y_range = Range1d(-20,20)
p.line(dt[1:], gpd, line_width=1)
p.circle(dt[1:], gpd, fill_color='white', size=4)

p.extra_y_ranges = {"temp": Range1d(start=-10, end=60)}
p.add_layout(LinearAxis(y_range_name="temp"), 'right')

p.line(dt, data['temperatuur'], color='green', y_range_name='temp')
p.circle(dt, data['temperatuur'], color='green', fill_color='white', size=4, y_range_name='temp')

output_file(os.path.join(outputdir, "Verbruik_Gas_per_dag.html"))
save(p)
show(p, browser=show_browser)





# Verbruik elektriciteit

e_total = data['edag'] + data['enacht']

p = figure(x_axis_label='Datum', x_axis_type='datetime', y_axis_label='Verbruik (kWh)', \
           plot_height=plot_height, plot_width=plot_width, title='Verbruik Elektriciteit')
p.line(dt, e_total)
p.circle(dt, e_total, size=3)

output_file(os.path.join(outputdir, "Verbruik_Elektriciteit.html"))
save(p)
show(p, browser=show_browser)





# Verbruik elektriciteit per dag

# Bereken het verbruik in elektriciteit tussen twee opeenvolgende metingen
# Elektriciteit voor de dag en nacht teller eerst bijeen tellen

e_total = data['edag'] + data['enacht']
e1 = e_total[0:-1]
e2 = e_total[1:]
e_diff = np.array(e2-e1)





# Bereken de totale opbrengst per dag van de zonnepanelen

z_total = data['sma_3000'] + data['sma_7000']

epd = e_diff + z_total[:-1] / dt_days
#epd = e_diff /dt_days + z_total[1:]



p = figure(x_axis_label='Datum', x_axis_type='datetime', y_axis_label='Verbruik (kWh/dag)', \
		   plot_height=plot_height, plot_width=plot_width, title='Verbruik Elektriciteit per dag')

p.line(dt[1:], epd, line_width=1)
p.circle(dt[1:], epd, fill_color='white', size=4)

output_file(os.path.join(outputdir, "Verbruik_Elektriciteit_per_dag.html"))
save(p)
show(p, browser=show_browser)


# Verschil tussen het berekende z_totaal en data['sma']

data_sma = data['sma']
where_isnan = np.isnan(data_sma)
data_sma[where_isnan] = 0.0

sma_diff = z_total - data_sma

small_values = sma_diff < 0.0001
sma_diff[small_values] = 0.0

df_data = {'DateTime': dt, 'sma': sma_diff}

df = pd.DataFrame(df_data)
df['tooltip'] = [x.strftime("%Y-%m-%d") for x in df['DateTime']]

source = ColumnDataSource(df.tail(10))

p = figure(x_axis_label='Datum', x_axis_type='datetime', y_axis_label='Calculated - Tabulated SMA', \
           plot_height=plot_height, plot_width=plot_width, title='Controle op berekening totale SMA', \
           tools='resize,pan,wheel_zoom,box_zoom,reset,previewsave,hover',logo=None)

hover = p.select(dict(type=HoverTool))
hover.tooltips = [('date','@tooltip'), ('value','@sma')]
hover.mode = 'mouse'

labels = LabelSet(x='DateTime', y='sma', text='sma', y_offset=8,
                  text_font_size="8pt", text_color="#555555",
                  source=source, text_align='center')
p.add_layout(labels)


p.line('DateTime', 'sma', line_width=1, source=source)
p.circle('DateTime', 'sma', fill_color='white', size=4, source=source)

output_file(os.path.join(outputdir, "Controle_SMA_berekening.html"))
save(p)
show(p, browser=show_browser)





# Verhouding opbrengst zonnepanelen

sma_ratio = data['sma_7000'] / data['sma_3000']

p = figure(x_axis_label='Datum', x_axis_type='datetime', y_axis_label='SMA 7000 / SMA 3000', \
           plot_height=plot_height, plot_width=plot_width, title='Verhouding SMA 7000 vs SMA 3000')

p.circle(dt, sma_ratio)

output_file(os.path.join(outputdir, "Ratio_Zonnepanelen.html"))
save(p)
show(p, browser=show_browser)


