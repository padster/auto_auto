# Scrape car listings from a bunch of sites into a dataframe.
# Saves the result to file for inspection.

import asyncio
import os
import pandas as pd

from datetime import datetime
from requests_html_modified import HTMLSession

# Per-site sources
from autotrader import AutotraderSource
from canada_drives import CanadaDrivesSource
from clutch import ClutchSource


# Whatever your preference - should make sure to narrow it down
# enough to not generate thousands of results.
FILTERS = {
    'min_year': 2019,
    'max_price': 22000,
}

### ALL!
def combineAll(opt):
    dataCD, _ = CanadaDrivesSource().runAll(opt)
    print ("  %d cars from Canada Drives" % len(dataCD))
    dataCL, _ = ClutchSource().runAll(opt)
    print ("+ %d cars from Clutch" % len(dataCL))
    dataAT, _ = AutotraderSource().runAll(opt)
    print ("+ %d cars from Autotrader" % len(dataAT))

    allDF = pd.concat([dataCD, dataCL, dataAT], ignore_index=True)
    allDF['date'] = datetime.today().strftime('%Y-%m-%d')
    return allDF

def runAndWrite():
    outPath = 'data/%s.csv' % datetime.today().strftime('%Y-%m-%d')
    if os.path.exists(outPath):
        print ("%s already exists!\nCopy/move the old one first" % outPath)
        return

    allDF = combineAll(FILTERS)
    allDF.to_csv(outPath)
    print ("\n\n-=-=-\nDone! Wrote %d cars\n\t%s" % (len(allDF), outPath))
    return allDF

df = runAndWrite()
print ("\n\n%d cars loaded into 'df'" % df.shape[0])
