#!/usr/bin/env python

import sys, re

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import matplotlib
matplotlib.style.use('ggplot')

import wordcloud as wc

import pdb # pdb.set_trace() when needed

RE_ALL_NUM = re.compile(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')
RE_START_INT = re.compile(r'^\d+') # Purposefully don't handle decimals

# Utility transformation functions

# Derive total hour slept by handling AM vs PM
def sleep_duration(row):
    sleep = row['Bed']
    wakeup = row['Wakeup']
    if sleep < wakeup:
        return wakeup - sleep
    return wakeup - (sleep - 12.0)

# Just a sum of every number found in a text blob, 0 otherwise
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

# Filter a list to only keep text matching a given hashtag
# IF None is passed in it will take everything
def extract_hashtag(field, hashtag):
    def get_hashtag_contents(row):
        if pd.notnull(row[field]):
            out = []
            pieces = row[field].split("\n")
            for piece in pieces:
                piece_clean = ''
                if hashtag is None: # Just take everything
                    piece_clean = piece.replace('- ', '').strip()
                elif hashtag in piece:
                    piece_clean = piece.replace(hashtag, '').replace('- ', '').strip()
                items = [x.strip() for x in piece_clean.split(", ")]
                # Add multiple times
                for item in items:
                    nums = RE_START_INT.findall(item)
                    nums = [int(x) for x in nums]
                    cnt = 1
                    if len(nums) > 0:
                        cnt = nums[0]
                    out.extend((RE_START_INT.sub('', item).strip(),) * cnt)
            return out
        else:
            return []
    return get_hashtag_contents

class Analyze:
    def __init__(self, fn):
        self.fn = fn

    def read_file(self):
        dtype_cols = {
            'Bed' : 'float64',
            'Wakeup' : 'float64',
            'Coffee' : 'float64',
            'Tea' : 'float64',
        }
        self.d = pd.read_csv(fn,
            dtype=dtype_cols,
            parse_dates=['Date',],
            index_col=0,
            low_memory=False)

    def add_cols(self):
        d = self.d

        d['SleepDuration'] = d.apply(sleep_duration, axis=1)
        d['Alcohol'] = d.apply(sum_all_nums('Drinks'), axis=1)
        d['Sodas'] = d.apply(sum_all_nums('Soda'), axis=1)
        d['Breakfast'] = d.apply(extract_hashtag('Food', '#breakfast'), axis=1)
        d['Lunch'] = d.apply(extract_hashtag('Food', '#lunch'), axis=1)
        d['Dinner'] = d.apply(extract_hashtag('Food', '#dinner'), axis=1)
        d['Snack'] = d.apply(extract_hashtag('Food', '#snack'), axis=1)
        d['DrinksList'] = d.apply(extract_hashtag('Drinks', None), axis=1)
        d['AlcoholLag'] = d['Alcohol'].shift()

    # Various plotting functions
    def generate_wordcloud(self, column):
        d = self.d

        text = " ".join([" ".join(x) for x in d[column]]).lower()

        wordcloud = wc.WordCloud(stopwords=None, mask=None,
            width=1000, height=1000, font_path=None,
            margin=10, relative_scaling=0.0,
            color_func=wc.random_color_func,
            background_color='black').generate(text)
        image = wordcloud.to_image()
        fn = ('wordcloud-' + column + '.png').lower()
        image.save(fn, format='png')

    def do_fit_and_plot(self, columns):
        d = self.d

        if len(columns) != 2:
            print 'Need to pass in two columns for now y, x'
            return

        y, x = columns

        print 'Fitting ', y, 'vs', x

        f = d.dropna(axis=0, how='any', subset=columns)

        plt.figure()
        ax = f.plot(kind='scatter', x=x, y=y)
        z = np.polyfit(x=f[x], y=f[y], deg=1, full=True)
        p = np.poly1d(z[0])
        f['fit'] = p(f[x])
        f.set_index(x, inplace=True)
        f['fit'].sort_index(ascending=False).plot(ax=ax)
        plt.gca().invert_xaxis()
        plt.savefig((x + '-vs-' + y + '.png').lower())
        plt.close()

        print z
        print p

        y_mean = np.sum(f['fit'])/len(f['fit'])
        ssr = np.sum((y_mean - f['fit'])**2)
        sst = np.sum((f[y] - f['fit'])**2)
        rsq = ssr / sst

        print rsq

    def plot_weekly(self):
        by_week = self.d.groupby(self.d.index.week).sum()
        print by_week.describe()
        plt.figure()
        by_week.boxplot(column=['Coffee', 'Tea', 'Alcohol', 'Sodas'])
        plt.savefig('coffee-tea-alcohol-soda-weekly.png')
        plt.close()

    def plot(self):
        self.plot_weekly()

        plt.figure()
        self.d.boxplot(column=['SleepDuration'])
        plt.savefig('sleep-duration.png')
        plt.close()

        plt.figure()
        self.d.boxplot(column=['Coffee', 'Tea', 'Alcohol', 'Sodas'])
        plt.savefig('coffee-tea-alcohol-soda-daily.png')
        plt.close()

        plt.figure()
        self.d.plot(kind='scatter', x='Alcohol', y='SleepDuration')
        plt.savefig('sleep-vs-alcohol.png')
        plt.close()

        # pdb.set_trace()

        self.do_fit_and_plot(['SleepDuration', 'Alcohol'])
        self.do_fit_and_plot(['SleepDuration', 'AlcoholLag'])

        self.generate_wordcloud('Breakfast')
        self.generate_wordcloud('Lunch')
        self.generate_wordcloud('Dinner')
        self.generate_wordcloud('Snack')
        self.generate_wordcloud('DrinksList')

    def run(self):
        self.read_file()

        print self.d
        print self.d.describe()

        self.add_cols()

        self.plot()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Specify a filename'
        exit(1)

    fn = sys.argv[1]
    a = Analyze(fn)
    a.run()
