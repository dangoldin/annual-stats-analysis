# annual-stats-analysis

I've been collecting various stats for each day over the past year and this is the code to analyze and visualize it.

## To run:
```
python analyze-v2.py stats2016.csv
```

## File format:
There's a sample file (sample-stats.csv) in this repo that has the appropriate columns with sample data but it's the following:

|Date|Bed|Wakeup|MoodMorning|MoodDay|MoodEvening|PhysicalMorning|PhysicalDay|PhysicalEvening|Food|Drinks|Coffee|Tea|Soda|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
1/1/2015|2|10|Congested|Good|Good|Lazy|Good|Good|"- Bagel + cream cheese + lox #breakfast
- Turkey sliders, salad #lunch
- Salad, beans, chickpeas, corn, turkey bacon, cheese #dinner"|- 1 beer|1|1|

## TODOs:
- Correlations with the moods
