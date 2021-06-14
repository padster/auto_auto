# Scrape car listings from a bunch of sites into a dataframe.
# Saves the result to file for inspection.

import asyncio
import os
import pandas as pd
import sys

from datetime import datetime
from requests_html_modified import HTMLSession

# Per-site sources
from autotrader import AutotraderSource
from canada_drives import CanadaDrivesSource
from clutch import ClutchSource

# Whatever your preference - should make sure to narrow it down
# enough to not generate thousands of results.
FILTERS = {
    'min_year': 2015,
    'max_year': 2017,
    'min_price': 30000,
    'max_price': 39999,
    'min_km': 40000,
    'max_km': 49999,
}

### ALL!
def combineAll(opt):
    session = HTMLSession(
        browser_args=["--no-sandbox", '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36']
    )

    dataCD = CanadaDrivesSource().runAll(session, opt)
    print ("  %d cars from Canada Drives" % len(dataCD))
    dataCL = ClutchSource().runAll(session, opt)
    print ("+ %d cars from Clutch" % len(dataCL))
    dataAT = AutotraderSource().runAll(session, opt)
    print ("+ %d cars from Autotrader" % len(dataAT))

    try:
        session.close()
    except Exception as ex:
        print (ex)

    allDF = pd.concat([dataCD, dataCL, dataAT], ignore_index=True)
    allDF['date'] = datetime.today().strftime('%Y-%m-%d')
    return allDF

def runAndWrite():
    outPath = 'data/%s.csv' % datetime.today().strftime('%Y-%m-%d')
    if os.path.exists(outPath):
        print ("%s already exists!\nCopy/move the old one first" % outPath)
        sys.exit(1)

    allDF = combineAll(FILTERS)
    allDF.to_csv(outPath, index=False, header=True)
    print ("\n\n-=-=-\nDone! Wrote %d cars\n\t%s" % (len(allDF), outPath))
    return allDF

df = runAndWrite()
#df, _ = CanadaDrivesSource().runAll(FILTERS)

print ("\n\n%d cars loaded into 'df'" % df.shape[0])
