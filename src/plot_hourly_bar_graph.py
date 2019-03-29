import matplotlib.pyplot as plt
from dateutil.parser import parse
import datetime
import csv
import numpy

list = []
x = []
y = []
bins_x = []

with open('../data/data.csv', 'r') as csvfile:
    plots = csv.reader((l.replace('\0', '') for l in csvfile))
    for row in plots:
        try:
            list.append([datetime.datetime.strptime(
                row[0], '%m/%d/%y %H:%M'), int(row[1])])
        except:
            pass

bins_x = []
bins_y = []

for element in list:
    if not element[0] in bins_x:
        bins_x.append(element[0])
        bins_y.append(0)

for i in range(0, len(list)):
    bin_index = bins_x.index(list[i][0])
    bins_y[bin_index] += list[i][1]

bins_hours = [element.hour for element in bins_x]

plt.bar(bins_hours, bins_y)
plt.xlabel('Hour') # x-axis label
plt.ylabel('Count') # y-axis label
plt.xticks(bins_hours, fontsize=10)
plt.title('Date') # plot title
plt.show()
