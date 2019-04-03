import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.pylab as pylab
from dateutil.parser import parse
import datetime
import csv
import numpy
import os


class CountReading:
    def __init__(self, timestamp, count):
        self.timestamp = timestamp
        self.count = count


# plotting params
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (12, 9),
          'axes.labelsize': 'x-large',
          'axes.titlesize': 'x-large',
          'xtick.labelsize': 'x-large',
          'ytick.labelsize': 'x-large'}
pylab.rcParams.update(params)

directory = os.path.join('..', 'graphs')
directory = os.path.join(directory, 'hourly_line_graph')
if not os.path.exists(directory):
    os.makedirs(directory)

data = []

with open(os.path.join(os.path.join('..', 'data'), 'data.csv'), 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for row in plots:
        try:
            data.append([datetime.datetime.strptime(
                row[0], '%Y-%m-%d %H:%M:%S.%f'), int(row[1])])
        except:
            pass

date_to_count_reading = {}
date_start_count = 0
current_date = datetime.datetime.min

for timestamp, count in data:
    if timestamp.date() not in date_to_count_reading:
        date_to_count_reading[timestamp.date()] = []
        # set the new date and count as the base
        current_date = timestamp.date()
        date_start_count = count
    date_to_count_reading[current_date].append(
        CountReading(timestamp, count-date_start_count))

# plot the daily graph
for date, count_reading_list in date_to_count_reading.items():
    x_axis = [count_reading.timestamp for count_reading in count_reading_list]
    y_axis = [count_reading.count for count_reading in count_reading_list]
    plt.plot(x_axis, y_axis, label=str(date)+' Count')
    plt.gca().xaxis.set_major_locator(dates.HourLocator())
    plt.gca().xaxis.set_major_formatter(dates.DateFormatter('%H'))  # format the hour
    # set the limit of x axis
    plt.gca().set_xlim([datetime.datetime.combine(date, datetime.time(hour=0)),
                        datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(hour=0))])
    plt.gca().set_ylim(bottom=0)  # set the limit of y axis
    plt.xlabel('Hour')  # x-axis label
    plt.ylabel('Count')  # y-axis label
    plt.title('Date: ' + str(date))  # plot title
    plt.legend()
    figure = plt.gcf()  # get current figure
    plt.savefig(os.path.join(directory, "%s.png" % str(date)), dpi=200)
    plt.close()

# plot the combined graph
for date, count_reading_list in date_to_count_reading.items():
    x_axis = [count_reading.timestamp for count_reading in count_reading_list]
    y_axis = [count_reading.count for count_reading in count_reading_list]
    plt.plot(x_axis, y_axis, label=str(date)+' Count')
    plt.xlabel('Hour')  # x-axis label
    plt.ylabel('Count')  # y-axis label
    plt.title('Pedestrian Counter Data')  # plot title
    plt.legend()
figure = plt.gcf()  # get current figure
plt.savefig(os.path.join(directory, "%s.png" % "combined"), dpi=200)
