# Copyright (c) 2015 Thomas Heller
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

import sys
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import collections

f = open(sys.argv[1], 'r')

benchmark = ''
threads = 1
window_size = 1
num_bytes = 1

data = {}

for line in f:
    line = line.replace('\n', '')
    if line.startswith('# OSU HPX'):
        if 'Latency' in line:
            benchmark = 'latency'
        if 'Bandwidth' in line:
            benchmark = 'bandwidth'
        continue
    if line.startswith('# OSU MPI'):
        if 'Latency' in line:
            benchmark = 'latency'
        if 'Bandwidth' in line:
            benchmark = 'bandwidth'
        window_size = 'MPI'
        threads = 1
        continue

    if line.startswith('threads='):
        strings = line.split(',')
        threads = 'HPX ({} cores)'.format(strings[0].split('=')[1])
        window_size = strings[1].split('=')[1]
        continue

    if len(line) < 1:
        continue

    if not line[0].isdigit():
        continue


    if not benchmark in data:
        data[benchmark] = collections.OrderedDict()
    t = data[benchmark]

    if not window_size in t:
        t[window_size] = collections.OrderedDict()
    t = t[window_size]

    if not threads in t:
        t[threads] = collections.OrderedDict()
    t = t[threads]

    strings = line.split(' ')
    numbytes = int(strings[0].strip())

    t[numbytes] = float(strings[-1].strip())

total = len(data['latency'])

html  = '<html>\n'
html += '<head><title>HPX OSU Microbenchmark results</title></head>\n'
html += '<body>\n'
html += '<h1><a name="top">HPX OSU Microbenchmark results</a></h1>\n'
html += '<p>Generated with <a href="http://sithhell.github.io/osu_benchmarks/plot.py">plot.py</a></p>\n'

html_images = ''
html_links = '<ul>\n'

for benchmark_key in data:
    benchmark = data[benchmark_key]
    for window_size in benchmark:
        if window_size == 'MPI':
            continue
        plot_data = benchmark[window_size];
        plot_data['MPI'] = benchmark['MPI'][1];
        df = pd.DataFrame(plot_data)#, columns=['blubb 1', '7',  '5', '4', '2', 'MPI'])
        title = benchmark_key + ', Window Size = {}'.format(window_size)
        ax = df.plot(marker = 'x')
        ax.set_title(title)
        ax.set_xlabel('Message Size (Bytes)')
        ax.set_ylabel('Latency (us)')

        plt.tight_layout()
        img = benchmark_key + '_window_size_{}.png'.format(window_size)
        plt.savefig('./' + img)
        html_links += '<li><a href=#{0}>{1}</a></li>\n'.format(img, title)
        html_images += '<p>\n'
        html_images += '<a name="{0}"><img src="{0}" alt="{1}"/></a><br/>\n'.format(img, title)
        html_images += '<a href=#top>Back to top</a>\n'
        html_images += '</p>\n'

html += html_links + '</ul>\n';
html += html_images;
html += '</body>\n'
html += '</html>\n'

f.close()
f = open('./osu_benchmark.html', 'w')
f.write(html)
f.close()
#plt.show()
