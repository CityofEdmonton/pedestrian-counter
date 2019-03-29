import matplotlib.pyplot as plt
from dateutil.parser import parse
import datetime
import csv
import numpy
import os

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
    plt.plot(value[0], value[1], label=str(key))
    plt.xlabel('Date') # x-axis label
    plt.ylabel('Count') # y-axis label
    plt.title('Pedestrian Counter Data') # plot title
    plt.legend()
    figure = plt.gcf() # get current figure
    figure.set_size_inches(8, 6)
    plt.savefig(r"%s\%s.png"%(directory, str(key)), dpi=200)
    plt.close()

# plot the combined graph
for key, value in date_dict.items():
    plt.plot(value[0], value[1], label=str(key))
    plt.xlabel('Date') # x-axis label
    plt.ylabel('Count') # y-axis label
    plt.title('Pedestrian Counter Data') # plot title
    plt.legend()
figure = plt.gcf() # get current figure
figure.set_size_inches(8, 6)
plt.savefig(r"%s\%s.png"%(directory, "combined"), dpi=200)