#!/usr/bin/python

import sys, csv

from collections import namedtuple, Counter

Row = namedtuple('Row', ('date','sleep','wakeup','physical_morning','physical_day','physical_evening','mood_morning','mood_day','mood_evening','food','drink','coffee','tea','soda'))

def sleep_duration(sleep, wakeup):
    sleep = float(sleep)
    wakeup = float(wakeup)
    if sleep < wakeup:
        return wakeup - sleep
    return wakeup - (sleep - 12.0)

def read_file(fn):
    with open(fn, 'r') as f:
        r = csv.reader(f, delimiter=',')
        r.next() # Skip header
        return [Row(*l) for l in r]

def count_dim(rows, dim):
    return Counter(getattr(r, dim) for r in rows)

def stats(d):
    s = sum(d)
    avg = s/len(d)
    max_ = max(d)
    min_ = min(d)

    s2 = sum((i-avg)*(i-avg) for i in d)
    var = s2/len(d)

    return {
        'total': s,
        'avg': avg,
        'max' : max_,
        'min' : min_,
        'var' : var,
    }

def summarize(rows):
    cnt_p_m = count_dim(rows, 'physical_morning')
    cnt_p_d = count_dim(rows, 'physical_day')
    cnt_p_e = count_dim(rows, 'physical_evening')
    cnt_m_m = count_dim(rows, 'mood_morning')
    cnt_m_d = count_dim(rows, 'mood_day')
    cnt_m_e = count_dim(rows, 'mood_evening')
    sleep_stats = stats([sleep_duration(r.sleep, r.wakeup) for r in rows])
    return {
        'p_m': cnt_p_m,
        'p_d': cnt_p_d,
        'p_e': cnt_p_e,
        'm_m': cnt_m_m,
        'm_d': cnt_m_d,
        'm_e': cnt_m_e,
        'sleep_stats': sleep_stats,
    }

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Specify a filename'
        exit(1)

    fn = sys.argv[1]
    rows = read_file(fn)

    print summarize(rows)
