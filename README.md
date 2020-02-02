# annual-stats-analysis

I've been collecting various stats for each day over the past year and this is the code to analyze and visualize it.

## To run:
```
python analyze-v2.py stats-2019.csv
```

## File format:
There's a sample file (sample-stats.csv) in this repo that has the appropriate columns with sample data but it's the following:

Date,Bed,Wakeup,Feeling,Producivity,Food,Drinks,Notes,Time Slept
2019-01-01,1/1/2019 5:03:14,1/1/2019 9:23:17,Good,,"- Egg, chicken #breakfast
- Chili chicken, noodles, salad #lunch
- Tortilla soup, pasta #dinner",- 2 coffee,,4.334166667

## TODOs:
- Better analysis of the moods (viz + correlations)
