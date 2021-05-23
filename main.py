#!/home/pat/code/python/anaconda/envs/carscrape/bin/python -i

# Scrape car listings from a bunch of sites into a dataframe.
# Saves the result to file for inspection.

import asyncio
import os
import pandas as pd

from datetime import datetime
from requests_html_modified import HTMLSession

# Whatever your preference - should make sure to narrow it down
# enough to not generate thousands of results.
FILTERS = {
    'min_year': 2018,
    'max_price': 18000,
}

# temporary - replace with above
MIN_YEAR = 2018
MAX_PRICE = 18000



def parseInt(s):
    return int(s.replace(',',''))

def carFromCanadaDrives(carElt):
    titles = carElt.find('.vehicle-card__title')
    if len(titles) != 2:
        print ("Match for year/make/model broken :(")
        return None
    yearAndMake = titles[0].text
    year, make = parseInt(yearAndMake[:4]), yearAndMake[5:]
    model = titles[1].text
    priceElt = carElt.find('.col-4')
    if len(priceElt) != 1:
        print ("Match for price broken :(")
        return None
    price = parseInt(priceElt[0].text[1:])
    miscElts = carElt.find('.col-6')
    if len(miscElts) < 2:
        print ("Match for KM broken")
        return None
    kmText = miscElts[-1].text
    if kmText[-3:] != ' KM':
        print ("Match for KM broken")
        return None
    km = parseInt(kmText[:-3])
    misc = miscElts[-2].text
    linkElts = carElt.find('.vehicle-card__link')
    if len(linkElts) != 1:
        print ("Link match not found")
        return None
    href = 'https://shop.canadadrives.ca%s' % linkElts[0].attrs['href']
    return {
        'price': price,
        'year': year,
        'make': make,
        'model': model,
        'km': km,
        'source': 'canada_drives',
        'link': href,
        'misc': misc,
    }

def canadaDrivesLoad():
    print ("Loading...\n\t%s" % CANADA_DRIVES_PATH)
    session = HTMLSession()
    page = session.get(CANADA_DRIVES_PATH)
    page.html.render(sleep=3, timeout=15)
    print ("Loaded!\n")
    return page


def canadaDrivesToPandas():
    page = canadaDrivesLoad()
    carElts = page.html.find('.vehicle-card')
    cars = [carFromCanadaDrives(elt) for elt in carElts]
    cars = [car for car in cars if car is not None]
    return pd.DataFrame(cars), page

## AUTOTRADER

AUTOTRADER_PATH = \
    "https://www.autotrader.ca/cars/bc/vancouver/?rcp={PAGE_SZ}&rcs={PAGE_START}&srt=9&" + \
    f"yRng={MIN_YEAR}%2C&pRng=%2C{MAX_PRICE}&prx=100&prv=British%20Columbia&loc=V6B0E6&" + \
    "trans=Automatic&hprc=True&wcp=True&sts=New-Used&adtype=Dealer&inMarket=advancedSearch"

def carFromAutoTrader(carElt):
    kmElts = carElt.find('.kms')
    if len(kmElts) != 1:
        print ("Skipping one, bad match for kms")
        return None
    kmText = kmElts[0].text
    if not (kmText.startswith('Mileage ') and kmText.endswith(' km')):
        print ("Skipping one, bad match for kms")
        return None
    km = parseInt(kmText[8:-3])
    priceElts = carElt.find('.price-amount')
    if len(priceElts) != 1:
        print ("Skipping one, bad match for price")
        return None
    price = parseInt(priceElts[0].text[1:])
    linkElts = carElt.find('.result-title')
    if len(linkElts) != 1:
        print ("Skipping one, bad match for link")
        return None
    href = 'https://www.autotrader.ca%s' % linkElts[0].attrs['href']
    yearMakeModel = linkElts[0].text
    yearMakeModelParts = yearMakeModel.split()
    year, make, model = yearMakeModelParts[:3]
    year = parseInt(year)
    misc = ' '.join(yearMakeModelParts[3:])
    return {
        'price': price,
        'year': year,
        'make': make,
        'model': model,
        'km': km,
        'source': 'autotrader',
        'link': href,
        'misc': misc,
    }

def autoTraderLoad(pageNum, pageSz):
    pagePath = AUTOTRADER_PATH.format(**{
        'PAGE_SZ': pageSz,
        'PAGE_START': pageNum * pageSz,
    })
    print ("Loading...\n\t%s" % pagePath)
    session = HTMLSession(browser_args=["--no-sandbox", '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'])
    page = session.get(pagePath)
    page.html.render(scrolldown=33, sleep=4, timeout=15)
    print ("Loaded!\n")
    return page

def autoTraderToPandas():
    allCars = []
    lastPage = None
    for pageNum in range(2):
        page = autoTraderLoad(pageNum, 100)
        carElts = page.html.find('.result-item')
        cars = [carFromAutoTrader(elt) for elt in carElts]
        cars = [car for car in cars if car is not None]
        lastPage = page
        allCars = allCars + cars
    return pd.DataFrame(allCars), page


## Clutch

CLUTCH_PATH = "https://www.clutch.ca/british-columbia?" + \
    f"priceHigh={MAX_PRICE}&transmissions=2&yearLow={MIN_YEAR}"

def carFromClutch(carElt):
    # Pretty hacky :(
    parts = carElt.text.split('\n')
    if len(parts) < 3:
        print ("UI text doesn't match")
        return None
    if parts[0] == 'Sold':
        print ("Car sold :(")
        return None

    yearMakeModel = parts[-3]
    yearMakeModelParts = yearMakeModel.split()
    year, make, model = yearMakeModelParts[:3]
    year = parseInt(year)
    misc = ' '.join(yearMakeModelParts[3:])

    if parts[-2][-3:] != ' km':
        print ("KM match doens't work")
        return None
    km = parseInt(parts[-2][:-3])

    if parts[-1][0] != '$':
        print ("Cost match doesn't work")
        return None
    price = parseInt(parts[-1][1:])

    linkElt = next(p for p in carElt.element.iterancestors())
    href = 'https://www.clutch.ca%s' % linkElt.get('href')

    return {
        'price': price,
        'year': year,
        'make': make,
        'model': model,
        'km': km,
        'source': 'clutch',
        'link': href,
        'misc': misc
    }

def clutchLoad():
    print ("Loading...\n\t%s" % CLUTCH_PATH)
    session = HTMLSession()
    page = session.get(CLUTCH_PATH)
    page.html.render(sleep=3, timeout=15)
    print ("Loaded!\n")
    return page

def clutchToPandas():
    page = clutchLoad()
    carElts = page.html.find('[data-element=VehicleCard]')
    cars = [carFromClutch(elt) for elt in carElts]
    cars = [car for car in cars if car is not None]
    return pd.DataFrame(cars), page

### ALL!
def combineAll():
    dataCD, _ = canadaDrivesToPandas()
    print ("  %d cars from Canada Drives" % len(dataCD))
    dataCL, _ = clutchToPandas()
    print ("+ %d cars from Clutch" % len(dataCL))
    dataAT, _ = autoTraderToPandas()
    print ("+ %d cars from AutoTrader" % len(dataAT))

    allDF = pd.concat([dataCD, dataCL, dataAT])
    allDF['date'] = datetime.today().strftime('%Y-%m-%d')
    return allDF

def runAndWrite():
    outPath = 'data/%s.csv' % datetime.today().strftime('%Y-%m-%d')
    if os.path.exists(outPath):
        print ("%s already exists!\nCopy/move the old one first" % outPath)
        return

    allDF = combineAll()
    allDF.to_csv(outPath)
    print ("\n\n-=-=-\nDone! Wrote %d cars\n\t%s" % (len(allDF), outPath))
    return allDF

#df = runAndWrite()
#print ("\n\n%d cars loaded into 'df'" % df.shape[0])
