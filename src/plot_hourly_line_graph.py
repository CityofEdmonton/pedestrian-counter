import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.pylab as pylab
from dateutil.parser import parse
import datetime
import csv
import numpy
import os

# plotting params
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (12, 9),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)

directory = r"..\graphs\hourly_line_graph"
if not os.path.exists(directory):
    os.makedirs(directory)

list = []

with open('../data/data.csv', 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for row in plots:
        try:
            list.append([datetime.datetime.strptime(
                row[0], '%Y-%m-%d %H:%M:%S.%f'), int(row[1])])
        except:
            pass

bins_x = set()
date_dict = {}
start_count = None
start_date = None

for element in list:
    if not element[0] in bins_x:
        bins_x.add(element[0])
        if start_date == element[0].date():
            date_dict[start_date][0].append(element[0])
            date_dict[start_date][1].append(element[1]-start_count)
        else:
            # set the new date and count as the base
            start_date = element[0].date()
            start_count = element[1]
            date_dict[start_date] = ([],[])
            date_dict[start_date][0].append(element[0])
            date_dict[start_date][1].append(element[1]-start_count)

# plot the daily graph
for key, value in date_dict.items():
    plt.plot(value[0], value[1], label=str(key)+' Count')
    plt.gca().xaxis.set_major_locator(dates.HourLocator())
    plt.gca().xaxis.set_major_formatter(dates.DateFormatter('%H')) # format the hour
    # set the limit of x axis
    plt.gca().set_xlim([datetime.datetime.combine(key, datetime.time(hour=0)), 
                        datetime.datetime.combine(key + datetime.timedelta(days=1), datetime.time(hour=0))])
    plt.xlabel('Hour') # x-axis label
    plt.ylabel('Count') # y-axis label
    plt.title('Date: ' + str(key)) # plot title
    plt.legend()
    figure = plt.gcf() # get current figure
    plt.savefig(r"%s\%s.png"%(directory, str(key)), dpi=200)
    plt.close()

# plot the combined graph
for key, value in date_dict.items():
    plt.plot(value[0], value[1], label=str(key)+' Count')
    plt.xlabel('Hour') # x-axis label
    plt.ylabel('Count') # y-axis label
    plt.title('Pedestrian Counter Data') # plot title
    plt.legend()
figure = plt.gcf() # get current figure
plt.savefig(r"%s\%s.png"%(directory, "combined"), dpi=200)