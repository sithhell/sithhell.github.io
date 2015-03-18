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


benchmark = ''
threads = 1
window_size = 1
num_bytes = 1

data = {}

for i in os.listdir(os.getcwd()):
    if i.endswith('.html') or i.endswith('png'):
        continue
    print('reading ' + str(i))
    f = open(i, 'r')
    cores = 0
    gflops = {}
    time = {}
    compute_time_inner = {}
    compute_time_outer = {}
    patch_provider_time = {}
    patch_accepter_time = {}
    perfctr = {}
    dim = []
    for line in f:
        line = line.replace('\n', '')

        p = re.compile('([0-9]+) cores')
        m = p.match(line)
        if m:
            cores = int(m.group(1))

        p = re.compile('dim: \(([0-9]+), ([0-9]+), ([0-9]+)\)')
        m = p.match(line)
        if m:
            dim = [int(m.group(1)), int(m.group(2)), int(m.group(3))]

        p = re.compile('Simulation Time\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)')
        m = p.match(line)
        if m:
            time['min'] = float(m.group(1))
            time['max'] = float(m.group(2))
            time['mean'] = float(m.group(3))
            time['stddev'] = float(m.group(4))

        p = re.compile('Compute Time Inner\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)')
        m = p.match(line)
        if m:
            compute_time_inner['min'] = float(m.group(1))
            compute_time_inner['max'] = float(m.group(2))
            compute_time_inner['mean'] = float(m.group(3))
            compute_time_inner['stddev'] = float(m.group(4))

        p = re.compile('Compute Time Ghost\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)')
        m = p.match(line)
        if m:
            compute_time_outer['min'] = float(m.group(1))
            compute_time_outer['max'] = float(m.group(2))
            compute_time_outer['mean'] = float(m.group(3))
            compute_time_outer['stddev'] = float(m.group(4))

        p = re.compile('PatchProviders Time\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)')
        m = p.match(line)
        if m:
            patch_provider_time['min'] = float(m.group(1))
            patch_provider_time['max'] = float(m.group(2))
            patch_provider_time['mean'] = float(m.group(3))
            patch_provider_time['stddev'] = float(m.group(4))

        p = re.compile('PatchAccepters Time\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)')
        m = p.match(line)
        if m:
            patch_accepter_time['min'] = float(m.group(1))
            patch_accepter_time['max'] = float(m.group(2))
            patch_accepter_time['mean'] = float(m.group(3))
            patch_accepter_time['stddev'] = float(m.group(4))

        p = re.compile('(/[a-z]+){locality\#[0-9]+/total}(\/[a-zA-Z\/\-_]+),[0-9]+,[0-9.]+,([\[\]a-z]+),([0-9.]+)(,([\[\]a-z]+))*')
        m = p.match(line)
        if m:
            name = m.group(1) + '{locality#*/total}' + m.group(2)
            if not name in perfctr:
                perfctr[name] = {'metric': m.group(6), 'value': 0.0}
            perfctr[name]['value'] = perfctr[name]['value'] + float(m.group(4))

    def gflops(time):
        cell_size = 128
        size = dim[0] * dim[1] * dim[2]
        flops = 27 * cell_size * cell_size * (3 + 6 + 1 + 6)
        return 200 * size * (flops / (time * 1000000000))

    print(str(cores) + ' ' + str(gflops(time['mean'])))

    data[cores] = {
            'time' : time
          , 'gflops' : {'min': gflops(time['max']), 'max': gflops(time['min']), 'mean': gflops(time['mean'])}
          , 'compute_time_inner' : compute_time_inner
          , 'compute_time_outer' : compute_time_outer
          , 'patch_provider_time' : patch_provider_time
          , 'patch_accepter_time' : patch_accepter_time
          , 'perfctr' : perfctr
        }


html  = '<html>\n'
html += '<head><title>LibgeoDecomp + HPX NBody Demo results</title></head>\n'
html += '<body>\n'
html += '<h1><a name="top">LibgeoDecomp + HPX NBody Demo results</a></h1>\n'
html += '<p>Generated with <a href="http://sithhell.github.io/nbody_demo/plot.py">plot.py</a></p>\n'

html_images = ''
html_links = '<ul>\n'

plot_data = {};
for cores in data:
    for stat in data[cores]['gflops']:
        if not stat in plot_data:
            plot_data[stat] = {}
        plot_data[stat][cores] = data[cores]['gflops'][stat]

df = pd.DataFrame(plot_data)
title = 'GFLOPS'
ax = df.plot(marker = 'x')
#ax.set_title(title)
ax.set_ylabel('GFLOPS')
ax.set_xlabel('cores')
plt.tight_layout()
img = 'gflops.png'
plt.savefig('./' + img)
html_links += '<li><a href=#{0}>{1}</a></li>\n'.format(img, title)
html_images += '<p>\n'
html_images += '<a name="{0}"><img src="{0}" alt="{1}"/></a><br/>\n'.format(img, title)
html_images += '<a href=#top>Back to top</a>\n'
html_images += '</p>\n'
plt.close()

plot_data = {'Compute Time' : {}, 'Communication Time' : {}};
for cores in data:
    plot_data['Compute Time'][cores] = data[cores]['compute_time_inner']['mean']
    plot_data['Compute Time'][cores] += data[cores]['compute_time_outer']['mean']
    plot_data['Communication Time'][cores] =  data[cores]['patch_provider_time']['mean']
    plot_data['Communication Time'][cores] += data[cores]['patch_accepter_time']['mean']

df = pd.DataFrame(plot_data)
title = 'Times'
ax = df.plot(marker = 'x')
ax.set_title(title)
ax.set_ylabel('time (seconds)')
ax.set_xlabel('cores')
plt.tight_layout()
img = 'times.png'
plt.savefig('./' + img)
html_links += '<li><a href=#{0}>{1}</a></li>\n'.format(img, title)
html_images += '<p>\n'
html_images += '<a name="{0}"><img src="{0}" alt="{1}"/></a><br/>\n'.format(img, title)
html_images += '<a href=#top>Back to top</a>\n'
html_images += '</p>\n'
plt.close()

for counter in data[data.keys()[0]]['perfctr'].keys():
    plot_data = {counter : {}}
    metric = data[data.keys()[0]]['perfctr'][counter]['metric']
    if metric == None:
        metric = ''
    for cores in data:
        plot_data[counter][cores] = data[cores]['perfctr'][counter]['value']

    df = pd.DataFrame(plot_data)
    title = counter
    ax = df.plot(marker = 'x')
    ax.set_title(title)
    ax.set_ylabel(metric)
    ax.set_xlabel('cores')
    plt.tight_layout()
    img = str(counter).replace('/', '_').replace('*', '_').replace('{', '_').replace('}', '_').replace('#', '_') + '.png'
    img = img[1:]
    plt.savefig('./' + img)
    html_links += '<li><a href=#{0}>{1}</a></li>\n'.format(img, title)
    html_images += '<p>\n'
    html_images += '<a name="{0}"><img src="{0}" alt="{1}"/></a><br/>\n'.format(img, title)
    html_images += '<a href=#top>Back to top</a>\n'
    html_images += '</p>\n'
    plt.close()

html += html_links + '</ul>\n';
html += html_images;
html += '</body>\n'
html += '</html>\n'

f.close()
f = open('./index.html', 'w')
f.write(html)
f.close()
