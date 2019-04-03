import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
from dateutil.parser import parse
import datetime
import csv
import numpy
import os
import copy


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
directory = os.path.join(directory, 'hourly_bar_graph')
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

# calculate the non-cumulative data by taking the difference
date_to_count_reading_noncumu = copy.deepcopy(date_to_count_reading)
for date, count_reading_list in date_to_count_reading.items():
    for i in range(1, len(count_reading_list)):
        # timestamps = [count_reading.timestamp for count_reading in count_reading_list]
        # counts = [count_reading.count for count_reading in count_reading_list]
        date_to_count_reading_noncumu[date][i].count = date_to_count_reading[date][i].count - \
            date_to_count_reading[date][i-1].count

for date, count_reading_list in date_to_count_reading_noncumu.items():
    # add up the counts into hourly bins
    bins_hours = set()
    hour_to_total_count = dict()
    for i in range(0, len(count_reading_list)):
        h = count_reading_list[i].timestamp.hour
        bins_hours.add(h)
        if h not in hour_to_total_count.keys():
            hour_to_total_count[h] = count_reading_list[i].count
        else:
            hour_to_total_count[h] += count_reading_list[i].count
    bins_hours = sorted(bins_hours)
    total_count_list = [count for hour,
                        count in sorted(hour_to_total_count.items())]

    # plot the daily graph
    plt.bar(bins_hours, total_count_list)
    plt.xlabel('Hour')  # x-axis label
    plt.ylabel('Count')  # y-axis label
    plt.xticks(bins_hours, fontsize=10)
    plt.title('Date: ' + str(date))  # plot title
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(8, 6)
    plt.savefig(os.path.join(directory, "%s.png" % str(date)), dpi=200)
    plt.close()
