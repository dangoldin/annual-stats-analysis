#!/usr/bin/python

import sys, re

import pandas as pd
import matplotlib.pyplot as plt

import pdb

RE_ALL_NUM = re.compile(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')

def read_file(fn):
    dtype_cols = {
        'Bed' : 'float64',
        'Wakeup' : 'float64',
        'Coffee' : 'float64',
        'Tea' : 'float64',
    }
    return pd.read_csv(fn,
        dtype=dtype_cols,
        parse_dates=['Date',],
        low_memory=False)

def sleep_duration(row):
    sleep = row['Bed']
    wakeup = row['Wakeup']
    if sleep < wakeup:
        return wakeup - sleep
    return wakeup - (sleep - 12.0)

def add_cols(d):
    d['SleepDuration'] = d.apply(sleep_duration,axis=1)
    return d

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Specify a filename'
        exit(1)

    fn = sys.argv[1]
    d = read_file(fn)
    d = add_cols(d)

    print d.describe()

    plt.figure()
    d.plot()
    plt.show()

    # print d

    # pdb.set_trace()
