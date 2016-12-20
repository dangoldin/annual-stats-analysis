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
        index_col=0,
        low_memory=False)

def sleep_duration(row):
    sleep = row['Bed']
    wakeup = row['Wakeup']
    if sleep < wakeup:
        return wakeup - sleep
    return wakeup - (sleep - 12.0)

def sum_all_nums(field):
    # Old but easier to debug the new one + test for nulls
    # return lambda x: sum(float(n[0]) for n in RE_ALL_NUM.findall(x[field]))
    def sum_row_vals(row):
        if pd.notnull(row[field]):
            nums = RE_ALL_NUM.findall(row[field])
            return sum(float(x[0]) for x in nums)
        else:
            return 0.0
    return sum_row_vals

def add_cols(d):
    d['SleepDuration'] = d.apply(sleep_duration, axis=1)
    d['Alcohol'] = d.apply(sum_all_nums('Drinks'), axis=1)
    # Just in case
    return d

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Specify a filename'
        exit(1)

    fn = sys.argv[1]
    d = read_file(fn)
    d = add_cols(d)

    print d.describe()

    # plt.figure()
    # d.plot()
    # plt.show()

    print d

    by_week = d.groupby(d.index.week).sum()

    print by_week.describe()

    plt.figure()
    by_week.boxplot(column=['Coffee', 'Tea', 'Alcohol'])
    plt.show()

    plt.figure()
    d.boxplot(column=['SleepDuration'])
    plt.show()

    # pdb.set_trace()
