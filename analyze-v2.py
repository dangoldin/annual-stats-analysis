#!/usr/bin/env python

import sys, re

import pandas as pd
import matplotlib.pyplot as plt

#import matplotlib
#matplotlib.style.use('ggplot')

import wordcloud as wc

import pdb # pdb.set_trace() when needed

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

def extract_hashtag(field, hashtag):
    def get_hashtag_contents(row):
        if pd.notnull(row[field]):
            out = []
            pieces = row[field].split("\n")
            for piece in pieces:
                if hashtag is None: # Just take everything
                    piece = piece.replace('- ', '').strip()
                    out.extend(piece.split(", "))
                elif hashtag in piece:
                    piece = piece.replace(hashtag, '').replace('- ', '').strip()
                    out.extend(piece.split(", "))
            return out
        else:
            return []
    return get_hashtag_contents

def add_cols(d):
    d['SleepDuration'] = d.apply(sleep_duration, axis=1)
    d['Alcohol'] = d.apply(sum_all_nums('Drinks'), axis=1)
    d['Breakfast'] = d.apply(extract_hashtag('Food', '#breakfast'), axis=1)
    d['Lunch'] = d.apply(extract_hashtag('Food', '#lunch'), axis=1)
    d['Dinner'] = d.apply(extract_hashtag('Food', '#dinner'), axis=1)
    d['Snack'] = d.apply(extract_hashtag('Food', '#snack'), axis=1)
    d['DrinksList'] = d.apply(extract_hashtag('Drinks', None), axis=1)
    # Return in case it's being assigned
    return d

def generate_wordcloud(d, column):
    text = " ".join([" ".join(x) for x in d[column]]).lower()

    wordcloud = wc.WordCloud(stopwords=None, mask=None,
        width=1000, height=1000, font_path=None,
        margin=10, relative_scaling=0.0,
        color_func=wc.random_color_func,
        background_color='black').generate(text)
    image = wordcloud.to_image()
    image.save('wordcloud-'+column+'.png', format='png')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Specify a filename'
        exit(1)

    fn = sys.argv[1]
    d = read_file(fn)
    d = add_cols(d)

    print d

    # plt.figure()
    # d.plot()
    # plt.show()

    print d.describe()

    by_week = d.groupby(d.index.week).sum()

    print by_week.describe()

    plt.figure()
    by_week.boxplot(column=['Coffee', 'Tea', 'Alcohol'])
    plt.savefig("coffee-tea-alcohol.png")
    plt.close()

    plt.figure()
    d.boxplot(column=['SleepDuration'])
    plt.savefig("sleep-duration.png")
    plt.close()

    generate_wordcloud(d, 'Breakfast')
    generate_wordcloud(d, 'Lunch')
    generate_wordcloud(d, 'Dinner')
    generate_wordcloud(d, 'Snack')
    generate_wordcloud(d, 'DrinksList')
