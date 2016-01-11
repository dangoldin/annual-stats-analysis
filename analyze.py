#!/usr/bin/python

import sys, csv

from collections import namedtuple

Row = namedtuple('Row', ('date','sleep','wakeup','physical_morning','physical_day','physical_evening','mood_morning','mood_day','mood_evening','food','drink','coffee','tea','soda'))

def read_file(fn):
    with open(fn, 'r') as f:
        r = csv.reader(f, delimiter=',')
        r.next() # Skip header
        return [Row(*l) for l in r]

def clean(row):
    pass

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Specify a filename'
        exit(1)

    fn = sys.argv[1]
    rows = read_file(fn)
    print rows
