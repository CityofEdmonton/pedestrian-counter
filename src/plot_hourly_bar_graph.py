import matplotlib.pyplot as plt
from dateutil.parser import parse
import datetime
import csv
import numpy
import os
import copy

directory = r"..\graphs\hourly_bar_graph"
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

# calculate the non-cumulative data by taking the difference
date_dict_noncumu = copy.deepcopy(date_dict)
for key, value in date_dict.items():
    for i in range(1,len(value[1])):
        date_dict_noncumu[key][1][i] = date_dict[key][1][i] - date_dict[key][1][i-1]

for key, value in date_dict_noncumu.items():
    # add up the counts into hourly bins
    bins_hours = set()
    bins_value = dict()
    for i in range(0,len(value[0])):
        h = value[0][i].hour
        bins_hours.add(h)
        if h not in bins_value.keys():
            bins_value[h] = value[1][i]
        else:
            bins_value[h] += value[1][i]
    bins_hours = sorted(bins_hours)
    bins_value = [x[1] for x in sorted(bins_value.items())]
    
    # plot the daily graph
    plt.bar(bins_hours, bins_value) 
    plt.xlabel('Hour') # x-axis label
    plt.ylabel('Count') # y-axis label
    plt.xticks(bins_hours, fontsize=10)
    plt.title('Date: ' + str(key)) # plot title
    figure = plt.gcf() # get current figure
    figure.set_size_inches(8, 6)
    plt.savefig(r"%s\%s.png"%(directory, str(key)), dpi=200)
    plt.close()
