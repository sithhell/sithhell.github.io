#!/usr/bin/python
# Copyright (c) 2015 Thomas Heller
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

import sys, os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import collections
import re
import csv

benchmark = ''

def counter_info(counter, header, idx):
    return ();

if len(sys.argv) == 2:
    benchmark = sys.argv[1]

print('reading counters.csv')
f = open('counters.csv', 'r')
header = f.readline().replace('\n', '').split(',')

counters = {};

def get_locality(counter_name):
    return re.findall('locality#\d+', counter_name)[0]

def get_name(counter_name, loc):
    return counter_name.replace('{' + loc + '/total}', '');

for h in header:
    loc = get_locality(h)
    counter_name = get_name(h, loc)
    if counter_name in counters:
        counters[counter_name][loc] = []
    else:
        counters[counter_name] = {};
        counters[counter_name][loc] = []


for line in f:
    data = line.replace('\n', '').split(',')
    for i in range(len(data)):
        h = header[i]
        loc = get_locality(h)
        counters[get_name(h, loc)][loc].append(float(data[i]));

html  = '<html>\n'
html += '<head><title>' + benchmark + '</title></head>\n'
html += '<body>\n'
html += '<h1><a name="top">' + benchmark + '</a></h1>\n'
html += '<p>Generated with <a href="http://sithhell.github.io/nbody_demo/plot.py">plot.py</a></p>\n'

html_images = ''
html_links = '<ul>\n'

for counter in sorted(counters):
    res = 0.0;
    for data in counters[counter]:
        res += sum(counters[counter][data])
    if res == 0.0:
        continue
    img_name = counter.replace('/', '_')[1:];
    img = img_name + '.png'
    title = counter
    html_links += '<li><a href=#{0}>{1}</a></li>\n'.format(img, title)
    html_images += '<p>\n'
    html_images += '<a name="{0}"><img src="{0}" alt="{1}"/></a><br/>\n'.format(img, title)
    html_images += '<a href=#top>Back to top</a>\n'
    html_images += '</p>\n'
    df = pd.DataFrame(counters[counter])
    ax = df.plot()#marker = 'x')
    ax.set_title(title)
    ax.set_xlabel('time')
    plt.tight_layout()
    plt.savefig('./' + img)
    plt.close()

html += html_links + '</ul>\n';
html += html_images;
html += '</body>\n'
html += '</html>\n'

f.close()
f = open('./index.html', 'w')
f.write(html)
f.close()
