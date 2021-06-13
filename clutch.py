# Car source for Clutch

import pandas as pd
import util

from requests_html_modified import HTMLSession

class ClutchSource:
    def path(self, opt):
        # TODO: optional params.
        return (
            "https://www.clutch.ca/british-columbia?" + \
            "priceHigh={max_price}&transmissions=2&yearLow={min_year}"
        ).format(**opt)

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
    def load(self, url):
        print ("Loading...\n\t%s" % url)
        session = HTMLSession()
        page = session.get(url)
        page.html.render(sleep=3, timeout=15)
        print ("Loaded!\n")
        return page

    def runAll(self, opt):
        url = self.path(opt)
        page = self.load(url)
        carElts = self.pageToElts(page)
        cars = [self.eltToCar(elt) for elt in carElts]
        cars = [car for car in cars if car is not None]
        return pd.DataFrame(cars), page
