import os
import datetime
import logme
import numpy as np
import pandas as pd

HOME_DIR = os.path.expanduser('~')

@logme.log
def load_data(logger=None):
    # Read the input csv file
    input_filename = 'Documents/PyCharmProjects/Meterstanden/Data/Meterstanden.csv'

    logger.info("Reading input csv file from {}.".format(input_filename))

    data = np.recfromcsv(os.path.join(HOME_DIR, input_filename))

    # Read the input csv file, make the Date_Time column the index column and parse the dates
    df = pd.read_csv(os.path.join(HOME_DIR, input_filename), index_col="Date_Time", parse_dates=True)

    # Convert the byte string b'' into a 'normal' string

    dt = np.array([datetime.datetime.strptime(x.decode('UTF-8'), '%Y-%m-%d %H:%M') for x in data['date_time']])

    return data, df, dt
