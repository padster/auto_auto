#!/home/pat/code/python/anaconda/envs/carscrape/bin/python -i

# Load all of the results scraped today into a dataframe for analysis.
# Also apply some basic filters to narrow down the results into a simpler
#    df to make it easier to quickly browse.

import pandas as pd
from datetime import datetime

# All data scraped today
TODAY_PATH = 'data/%s.csv' % datetime.today().strftime('%Y-%m-%d')
allDF = pd.read_csv(TODAY_PATH)
print ("%d cars loaded into 'allDF'" % allDF.shape[0])

# Whatever you want can go here to narrow down the preferences.
df = allDF.copy()
df = df[df.km < 40000]
df = df[df.make != 'Chevrolet']
df = df[df.make != 'Nissan']
df = df[df.make != 'Kia']
df = df[df.make != 'Mitsubishi']
df = df[df.make != 'Ford']
print ("Filtered to 'df' (%d cars)" % df.shape[0])
