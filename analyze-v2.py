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
    return (wakeup - sleep).seconds / 3600.0

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
            return [o.strip().lower() for o in out if o != '']
        else:
            return []
    return get_hashtag_contents

def count_values(field, value):
    def get_value_counts(row):
        total = 0.0
        for piece in row[field]:
            if value in piece:
                nums = RE_ALL_NUM.findall(piece)
                if len(nums):
                    total += float(nums[0][0])
                else:
                    total += 1.0
        return total
    return get_value_counts

class Analyze:
    def __init__(self, fn):
        self.fn = fn

    def read_file(self):
        self.d = pd.read_csv(fn,
            parse_dates=['Date', 'Bed', 'Wakeup'],
            index_col=0,
            low_memory=False)

    def add_cols(self):
        d = self.d

        d['SleepDuration'] = d.apply(sleep_duration, axis=1)
        d['Breakfast'] = d.apply(extract_hashtag('Food', '#breakfast'), axis=1)
        d['Lunch'] = d.apply(extract_hashtag('Food', '#lunch'), axis=1)
        d['Dinner'] = d.apply(extract_hashtag('Food', '#dinner'), axis=1)
        d['Snack'] = d.apply(extract_hashtag('Food', '#snack'), axis=1)
        d['DrinksList'] = d.apply(extract_hashtag('Drinks', None), axis=1)

        d['Coffee'] = d.apply(count_values('DrinksList', 'coffee'), axis=1)
        d['Tea'] = d.apply(count_values('DrinksList', 'tea'), axis=1)

        d['Coke'] = d.apply(count_values('DrinksList', 'coke'), axis=1)

        d['Beer'] = d.apply(count_values('DrinksList', 'beer'), axis=1)
        d['Wine'] = d.apply(count_values('DrinksList', 'wine'), axis=1)
        d['Cocktail'] = d.apply(count_values('DrinksList', 'cocktail'), axis=1)
        d['Alcohol'] = d['Beer'] + d['Wine'] + d['Cocktail']
        d['AlcoholLag'] = d['Alcohol'].shift()

    # Various plotting functions
    def generate_wordcloud(self, column):
        d = self.d

        # Strip out numbers and extra spaces
        text = " ".join([" ".join(x) for x in d[column]]).lower().replace('.', ' ')
        text = re.sub('\d+',' ',text)
        text = re.sub('\s+',' ',text)

        text = " ".join(sorted(text.split(" ")))

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
            print('Need to pass in two columns for now y, x')
            return

        y, x = columns

        print('Fitting ', y, 'vs', x)

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

        print(z)
        print(p)

        y_mean = np.sum(f['fit'])/len(f['fit'])
        ssr = np.sum((y_mean - f['fit'])**2)
        sst = np.sum((f[y] - f['fit'])**2)
        rsq = ssr / sst

        print(rsq)

    def plot_weekly(self):
        by_week = self.d.groupby(self.d.index.week).sum()
        print(by_week.describe())
        plt.figure()
        by_week.boxplot(column=['Coffee', 'Tea', 'Alcohol', 'Coke'])
        plt.savefig('coffee-tea-alcohol-coke-weekly.png')
        plt.close()

    def plot(self):
        self.plot_weekly()

        plt.figure()
        self.d.boxplot(column=['SleepDuration'])
        plt.savefig('sleep-duration.png')
        plt.close()

        plt.figure()
        self.d.boxplot(column=['Coffee', 'Tea', 'Alcohol', 'Coke'])
        plt.savefig('coffee-tea-alcohol-coke-daily.png')
        plt.close()

        plt.figure()
        self.d.plot(kind='scatter', x='Alcohol', y='SleepDuration')
        plt.savefig('sleep-vs-alcohol.png')
        plt.close()

        self.do_fit_and_plot(['SleepDuration', 'Alcohol'])
        self.do_fit_and_plot(['SleepDuration', 'AlcoholLag'])

        for col in ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'DrinksList']:
            self.generate_wordcloud(col)

    def run(self):
        self.read_file()

        print('Before column addition')
        print(self.d)
        print(self.d.describe())

        self.add_cols()

        print('After column addition')
        print(self.d)
        print(self.d.describe())

        print('Starting plots')
        self.plot()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Specify a filename')
        exit(1)

    fn = sys.argv[1]
    a = Analyze(fn)
    a.run()
