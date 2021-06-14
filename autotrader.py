# Load car options from Canada Drives

from urllib.parse import urlencode

import pandas as pd
import util

from requests_html_modified import HTMLSession

class AutotraderSource:
    N_PAGES = 1
    PAGE_SZ = 100

    def maybeQueryRange(self, opt, queryParams, optKey, queryKey):
        minKey, maxKey = f'min_{optKey}', f'max_{optKey}'
        hasMin, hasMax = minKey in opt, maxKey in opt
        if hasMin or hasMax:
            queryParams[queryKey] = ','.join([
                str(opt.get(minKey, '')),
                str(opt.get(maxKey, ''))
            ])

    def path(self, opt):
        # TODO: optional params.
        queryParams = {
            'trans': 'Automatic',
            'loc': 'V5N2T2',
            'srt': 9,
            'prv': 'British%20Columbia',
            'prx': 100,
            'hprc': 'True',
            'wcp': 'True',
            'sts': 'Used',
            'adtype': 'Dealer',
            'inMarket': 'advancedSearch',
            'rcp': '{page_sz}'.format(**opt),
            'rcs': '{page_sz}'.format(**opt),
        }
        self.maybeQueryRange(opt, queryParams, 'year', 'yRng')
        self.maybeQueryRange(opt, queryParams, 'km', 'oRng')
        self.maybeQueryRange(opt, queryParams, 'price', 'pRng')

        parts = ['cars']
        if 'make' in opt:
            parts.append(opt['make'].lower())
            if 'model' in opt:
                parts.append(opt['model'].lower())
        parts.append('bc')
        parts.append('vancouver')
        return "https://www.autotrader.ca/" + '/'.join(parts) + '/?' + urlencode(queryParams)

    # CarElt -> Car
    def eltToCar(self, carElt):
        kmElts = carElt.find('.kms')
        if len(kmElts) != 1:
            print ("Skipping one, bad match for kms")
            return None
        kmText = kmElts[0].text
        if not (kmText.startswith('Mileage ') and kmText.endswith(' km')):
            print ("Skipping one, bad match for kms")
            return None
        km = util.parseInt(kmText[8:-3])
        priceElts = carElt.find('.price-amount')
        if len(priceElts) != 1:
            print ("Skipping one, bad match for price")
            return None
        price = util.parseInt(priceElts[0].text[1:])
        linkElts = carElt.find('.result-title')
        if len(linkElts) != 1:
            print ("Skipping one, bad match for link")
            return None
        href = 'https://www.autotrader.ca%s' % linkElts[0].attrs['href']
        yearMakeModel = linkElts[0].text
        yearMakeModelParts = yearMakeModel.split()
        year, make, model = yearMakeModelParts[:3]
        year = util.parseInt(year)
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

    # Page -> carelt*
    def pageToElts(self, page):
        return page.html.find('.result-item')

    # URL -> Page
    def load(self, session, url):
        print ("Loading...\n\t%s" % url)
        page = session.get(url)
        page.html.render(scrolldown=33, sleep=4, timeout=15)
        print ("Loaded!\n")
        return page

    def runAll(self, session, opt):
        allCars = []

        for pageNum in range(self.N_PAGES):
            pageOpt = {
                **opt,
                'page_sz': self.PAGE_SZ,
                'page_start': pageNum * self.PAGE_SZ,
            }
            url = self.path(pageOpt)
            page = self.load(session, url)
            carElts = self.pageToElts(page)
            cars = [self.eltToCar(elt) for elt in carElts]
            cars = [car for car in cars if car is not None]
            page.close()

        return pd.DataFrame(cars)
