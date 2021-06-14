# Car source for Clutch

from urllib.parse import urlencode

import pandas as pd
import util

from requests_html_modified import HTMLSession

CLUTCH_MAKE_TO_ID = {
    'Honda': 14,
    'Kia': 5,
    'Mazda': 2,
    'Toyota': 6,
    'Volkswagen': 13,
}

CLUTCH_MODEL_TO_ID = {
    'Corolla': 7,
    'Highlander': 83,
    'Odyssey': 90,
    'Pilot': 229,
    'Sienna': 16,
    'Soul': 6,
}

class ClutchSource:
    def addMakeModelToQuery(self, opt, params):
        # Yuck. Done as ID lookups, not as text strings.
        # Model ID should be unique?
        if 'make' in opt:
            if opt['make'] in CLUTCH_MAKE_TO_ID:
                params['makes'] = CLUTCH_MAKE_TO_ID[opt['make']]
            else:
                raise Exception(f"Unknown make: {opt['make']}, please look up on Clutch and add to CLUTCH_MAKE_TO_ID")
        if 'model' in opt:
            if opt['model'] in CLUTCH_MODEL_TO_ID:
                params['models'] = CLUTCH_MODEL_TO_ID[opt['model']]
            else:
                raise Exception(f"Unknown model: {opt['model']}, please look up on Clutch and add to CLUTCH_MODEL_TO_ID")

    def maybeQueryRange(self, opt, queryParams, optKey, queryKey):
        minKey, maxKey = f'min_{optKey}', f'max_{optKey}'
        if minKey in opt:
            queryParams[f'{queryKey}Low'] = opt[minKey]
        if maxKey in opt:
            queryParams[f'{queryKey}High'] = opt[maxKey]

    def path(self, opt):
        queryParams = {
            'transmissions': 2,
            'priceHigh': '{max_price}'.format(**opt),
            'yearLow': '{min_year}'.format(**opt),
        }
        self.maybeQueryRange(opt, queryParams, 'year', 'year')
        self.maybeQueryRange(opt, queryParams, 'km', 'mileage')
        self.maybeQueryRange(opt, queryParams, 'price', 'price')

        if 'min_km' in opt:
            queryParams['mileageLow'] = opt['min_km']
        if 'max_km' in opt:
            queryParams['mileageHigh'] = opt['max_km']

        self.addMakeModelToQuery(opt, queryParams)
        return "https://www.clutch.ca/british-columbia?" + urlencode(queryParams)

    # CarElt -> Car
    def eltToCar(self, carElt):
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
        year = util.parseInt(year)
        misc = ' '.join(yearMakeModelParts[3:])

        if parts[-2][-3:] != ' km':
            print ("KM match doens't work")
            return None
        km = util.parseInt(parts[-2][:-3])

        if parts[-1][0] != '$':
            print ("Cost match doesn't work")
            return None
        price = util.parseInt(parts[-1][1:])

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

    # Page -> carelt*
    def pageToElts(self, page):
        return page.html.find('[data-element=VehicleCard]')

    # URL -> Page
    def load(self, session, url):
        print ("Loading...\n\t%s" % url)
        page = session.get(url)
        page.html.render(sleep=15, timeout=15)
        print ("Loaded!\n")
        return page

    def runAll(self, session, opt):
        url = self.path(opt)
        page = self.load(session, url)
        carElts = self.pageToElts(page)
        cars = [self.eltToCar(elt) for elt in carElts]
        cars = [car for car in cars if car is not None]
        page.close()
        return pd.DataFrame(cars)
