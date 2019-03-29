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
        bins_y.append(element[1])

plt.plot(bins_x, bins_y, label='Data')
plt.xlabel('Date') # x-axis label
plt.ylabel('Count') # y-axis label
plt.title('Pedestrian Counter Data') # plot title
plt.legend()
plt.show()
