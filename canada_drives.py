# Load car options from Canada Drives

from urllib.parse import urlencode

import pandas as pd
import util

from requests_html_modified import HTMLSession

class CanadaDrivesSource:
    def path(self, opt):
        queryParams = {
            'region': 'BC',
            'sort_by': 'just_listed',
            'transmission': 'automatic',
            'product_price': '0_{max_price}'.format(**opt),
            'year': '{min_year}'.format(**opt),
        }
        if 'make' in opt:
            queryParams['make'] = opt['make']
        if 'model' in opt:
            queryParams['model'] = opt['model']
        return "https://shop.canadadrives.ca/cars/bc?" + urlencode(queryParams)

    # CarElt -> Car
    def eltToCar(self, carElt):
        titles = carElt.find('.vehicle-card__title')
        if len(titles) != 2:
            print ("Match for year/make/model broken :(")
            return None
        yearAndMake = titles[0].text
        year, make = util.parseInt(yearAndMake[:4]), yearAndMake[5:]
        model = titles[1].text
        priceElt = carElt.find('.col-4')
        if len(priceElt) != 1:
            print ("Match for price broken :(")
            return None
        price = util.parseInt(priceElt[0].text[1:])
        miscElts = carElt.find('.col-6')
        if len(miscElts) < 2:
            print ("Match for KM broken")
            return None
        kmText = miscElts[-1].text
        if kmText[-3:] != ' KM':
            print ("Match for KM broken")
            return None
        km = util.parseInt(kmText[:-3])
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

    # Page -> carelt*
    def pageToElts(self, page):
        return page.html.find('.vehicle-card')

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
